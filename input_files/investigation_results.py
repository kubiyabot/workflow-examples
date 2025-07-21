#!/usr/bin/env python3
import os
import json
import requests
import re
from datetime import datetime

def extract_summary(text, section_name):
    """Extract summary from investigation text"""
    try:
        # Look for SUMMARY_FOR_SLACK section
        pattern = r'SUMMARY_FOR_SLACK:(.*?)(?=\n\n|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            summary = match.group(1).strip()
            # Clean up the summary
            summary = ' '.join(summary.split())
            # Remove any special characters that might cause issues
            summary = re.sub(r'[^a-zA-Z0-9 .,:-]', '', summary)
            return summary
        return f"{section_name} completed - see uploaded file for details"
    except:
        return f"{section_name} completed - see uploaded file for details"

def extract_tldr_summary(report_text):
    """Extract TLDR summary from the formatted report"""
    try:
        # Look for the TLDR section
        tldr_pattern = r'## 📋 TLDR - EXECUTIVE SUMMARY(.*?)(?=##|---)'
        match = re.search(tldr_pattern, report_text, re.DOTALL)
        if match:
            tldr_content = match.group(1).strip()
            # Extract key findings
            key_findings = []
            lines = tldr_content.split('\n')
            for line in lines:
                if '**Root Cause**:' in line:
                    key_findings.append(line.replace('**', '').replace('- ', ''))
                elif '**Impact**:' in line:
                    key_findings.append(line.replace('**', '').replace('- ', ''))
                elif '**Current Status**:' in line:
                    key_findings.append(line.replace('**', '').replace('- ', ''))
            return ' | '.join(key_findings) if key_findings else "Investigation complete - see report for details"
        return "Investigation complete - see report for details"
    except:
        return "Investigation complete - see report for details"

def upload_file_to_slack(token, channel, filename, title, content):
    """Upload a file to Slack silently (no message posted)"""
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        # Upload file using files.upload but without initial_comment to prevent message
        # The key is to NOT include initial_comment parameter
        files = {
            'file': (filename, content.encode('utf-8'), 'text/markdown')
        }
        data = {
            'channels': channel,
            'title': title,
            'filename': filename,
            'filetype': 'markdown'
            # NO initial_comment parameter - this is what causes the message to be posted
        }
        response = requests.post('https://slack.com/api/files.upload',
                               headers=headers,
                               data=data,
                               files=files)
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✅ Successfully uploaded {filename} (no message posted)")
                return result.get('file', {})
            else:
                print(f"❌ Failed to upload {filename}: {result.get('error')}")
                return None
        else:
            print(f"❌ HTTP error uploading {filename}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception uploading {filename}: {e}")
        return None

def post_summary_message(token, channel, incident_info, main_report_file, cluster_file, service_file, tldr_summary):
    """Post a summary message with buttons"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    severity_emoji = {
        'critical': '🚨',
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    }.get(incident_info['severity'].lower(), '⚠️')
    # Build file references
    file_refs = []
    if main_report_file:
        file_refs.append(f"📋 <{main_report_file.get('permalink', '#')}|Executive Summary>")
    if cluster_file:
        file_refs.append(f"🏗️ <{cluster_file.get('permalink', '#')}|Cluster Health Summary>")
    if service_file:
        file_refs.append(f"🎯 <{service_file.get('permalink', '#')}|Service Analysis Summary>")
    files_section = "\n".join(file_refs) if file_refs else "No investigation files available"
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "✅ AI INVESTIGATION COMPLETE"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Incident:*\n{incident_info['id']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Severity:*\n{severity_emoji} {incident_info['severity']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Services:*\n{incident_info['services']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Title:*\n{incident_info['title']}"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🎯 Key Findings:*\n{tldr_summary}"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📄 Investigation Reports:*\n{files_section}\n\n_Investigation completed at {timestamp}_"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔍 Deep Dive Analysis",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": json.dumps({
                        "agent_uuid": incident_info['agent_uuid'],
                        "message": incident_info.get('deep_dive_prompt', f"DEEP DIVE ANALYSIS - Analyzing incident {incident_info['id']}: {incident_info['title']}. Affected services: {incident_info['services']}. I will perform deep analysis using available metrics and datasets. I'll focus on root cause analysis, performance metrics, and provide detailed recommendations.")
                    }),
                    "action_id": "agent.process_message_1"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔧 Apply Fixes",
                        "emoji": True
                    },
                    "style": "danger",
                    "value": json.dumps({
                        "agent_uuid": incident_info['agent_uuid'],
                        "message": incident_info.get('apply_fixes_prompt', f"APPLY FIXES - Ready to apply remediation for incident {incident_info['id']}: {incident_info['title']}. Affected services: {incident_info['services']}. I have reviewed the investigation findings and will help apply fixes. Please confirm which fixes you'd like me to apply or provide specific remediation instructions.")
                    }),
                    "action_id": "agent.process_message_2"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Monitor Recovery",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": json.dumps({
                        "agent_uuid": incident_info['agent_uuid'],
                        "message": incident_info.get('monitoring_prompt', f"MONITORING RECOVERY - Tracking recovery for incident {incident_info['id']}: {incident_info['title']}. Services: {incident_info['services']}. I will monitor service health, check metrics, and verify that applied fixes are working correctly.")
                    }),
                    "action_id": "agent.process_message_3"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📋 View Incident",
                        "emoji": True
                    },
                    "url": incident_info['url']
                }
            ]
        }
    ]
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'channel': channel,
        'text': '✅ AI Investigation Complete',
        'blocks': blocks
    }
    try:
        response = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=payload)
        if response.status_code == 200 and response.json().get('ok'):
            print("✅ Summary message posted successfully to Slack")
            return True
        else:
            error_msg = response.json().get('error', 'Unknown error')
            print(f"❌ Failed to post summary: {error_msg}")
            return False
    except Exception as e:
        print(f"❌ Error posting summary: {e}")
        return False

def main():
    # Get Slack token
    slack_token = os.getenv('slack_token_value', '')
    if not slack_token:
        print("❌ Error: Slack token not provided")
        return
    # Get parameters
    incident_info = {
        'id': os.getenv('incident_id', ''),
        'title': os.getenv('incident_title', ''),
        'severity': os.getenv('incident_severity', ''),
        'services': os.getenv('affected_services', ''),
        'url': os.getenv('incident_url', ''),
        'agent_uuid': os.getenv('agent_uuid', ''),
        'deep_dive_prompt': os.getenv('deep_dive_prompt', ''),
        'apply_fixes_prompt': os.getenv('apply_fixes_prompt', ''),
        'monitoring_prompt': os.getenv('monitoring_prompt', '')
    }
    slack_channel_id = os.getenv('slack_channel_id', '')
    # Get investigation results
    cluster_results = os.getenv('cluster_results', '')
    service_results = os.getenv('service_results', '')
    formatted_report = os.getenv('formatted_report', '')
    # Get LLM-generated summaries
    executive_summary_str = os.getenv('executive_summary', '')
    formatted_summaries_str = os.getenv('formatted_summaries', '')
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    # Parse the executive summary JSON
    try:
        executive_summary = json.loads(executive_summary_str)
        tldr_summary = executive_summary.get('slack_summary', 'Investigation complete - see report for details')
        print(f"📊 Using LLM-generated TLDR summary: {tldr_summary}")
    except:
        # Fallback to extracting from formatted report
        tldr_summary = extract_tldr_summary(formatted_report)
        print(f"📊 Fallback - Extracted TLDR summary: {tldr_summary}")
    # Extract summaries from formatted_summaries
    cluster_summary = 'Cluster investigation completed - see uploaded file for details'
    service_summary = 'Service investigation completed - see uploaded file for details'
    if formatted_summaries_str:
        # Extract cluster and service summaries from the LLM output
        cluster_match = re.search(r'## CLUSTER_HEALTH_SUMMARY(.*?)## SERVICE_INVESTIGATION_SUMMARY', formatted_summaries_str, re.DOTALL)
        service_match = re.search(r'## SERVICE_INVESTIGATION_SUMMARY(.*?)$', formatted_summaries_str, re.DOTALL)
        if cluster_match:
            cluster_summary = cluster_match.group(1).strip()
        if service_match:
            service_summary = service_match.group(1).strip()
    # Upload main formatted report with TLDR
    main_report_file = None
    if formatted_report:
        print("📤 Uploading main executive report with TLDR (silently)...")
        main_report_file = upload_file_to_slack(
            slack_token,
            slack_channel_id,
            f"incident_report_{incident_info['id']}.md",
            f"Executive Incident Report - {incident_info['title']}",
            formatted_report
        )
    # Prepare cluster investigation technical report
    cluster_report = f"""# Cluster Health Investigation - Technical Details\n\n**Incident:** {incident_info['id']} - {incident_info['title']}\n**Generated:** {timestamp} UTC\n**Severity:** {incident_info['severity']}\n\n## Summary\n{cluster_summary}\n\n## Full Technical Investigation Results\n\n{cluster_results}\n"""
    # Prepare service investigation technical report
    service_report = f"""# Service-Specific Investigation - Technical Details\n\n**Incident:** {incident_info['id']} - {incident_info['title']}\n**Generated:** {timestamp} UTC\n**Affected Services:** {incident_info['services']}\n**Severity:** {incident_info['severity']}\n\n## Summary\n{service_summary}\n\n## Full Technical Investigation Results\n\n{service_results}\n"""
    # Upload technical investigation files
    cluster_file = None
    service_file = None
    if cluster_results:
        print("📤 Uploading cluster investigation technical details (silently)...")
        cluster_file = upload_file_to_slack(
            slack_token,
            slack_channel_id,
            f"cluster_tech_details_{incident_info['id']}.md",
            f"Cluster Health Technical Details - {incident_info['title']}",
            cluster_report
        )
    if service_results:
        print("📤 Uploading service investigation technical details (silently)...")
        service_file = upload_file_to_slack(
            slack_token,
            slack_channel_id,
            f"service_tech_details_{incident_info['id']}.md",
            f"Service Technical Details - {incident_info['services']}",
            service_report
        )
    # Post summary message with TLDR and buttons
    print("📨 Posting summary message with TLDR...")
    success = post_summary_message(slack_token, slack_channel_id, incident_info, main_report_file, cluster_file, service_file, tldr_summary)
    if success:
        print("\n✅ All investigation results uploaded and summary posted successfully!")
    else:
        print("\n⚠️ Some operations may have failed. Check the logs above.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

