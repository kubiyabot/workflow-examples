#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime


def main():
    # Get parameters
    slack_token = os.getenv('slack_token')
    channel = os.getenv('channel')
    incident_id = os.getenv('incident_id')
    incident_title = os.getenv('incident_title')
    incident_severity = os.getenv('incident_severity')
    affected_services = os.getenv('affected_services')

    # Get investigation results
    executive_summary_str = os.getenv('executive_summary', '{}')
    formatted_report = os.getenv('formatted_report', '')
    na_results = os.getenv('na_results', '')
    eu_results = os.getenv('eu_results', '')

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    # Parse executive summary
    try:
        executive_summary = json.loads(executive_summary_str)
        tldr_summary = executive_summary.get('slack_summary', 'Investigation complete - see detailed reports')
    except:
        tldr_summary = 'Investigation complete - see detailed reports'

    # Severity emoji
    severity_emoji = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }.get(incident_severity.lower(), '⚪')

    headers = {
        'Authorization': f'Bearer {slack_token}'
    }

    file_urls = []

    # Upload main report
    if formatted_report:
        files = {
            'file': (f'incident_report_{incident_id}.md', formatted_report.encode('utf-8'), 'text/markdown')
        }
        data = {
            'channels': channel,
            'title': f'Incident Report - {incident_title}',
            'filename': f'incident_report_{incident_id}.md',
            'filetype': 'markdown'
        }
        response = requests.post('https://slack.com/api/files.upload', headers=headers, data=data, files=files)
        if response.status_code == 200 and response.json().get('ok'):
            file_url = response.json().get('file', {}).get('permalink', '#')
            file_urls.append(f'📄 <{file_url}|Full Incident Report>')
            print('✅ Main report uploaded')

    # Upload NA results
    if na_results:
        na_report = f"""# NA Production Investigation
        
        **Incident:** {incident_id} - {incident_title}
        **Generated:** {timestamp}
        **Region:** North America (NA)
        
        ## Investigation Results

        {na_results}
        """

        files = {
            'file': (f'na_investigation_{incident_id}.md', na_report.encode('utf-8'), 'text/markdown')
        }
        data = {
            'channels': channel,
            'title': f'NA Investigation - {incident_title}',
            'filename': f'na_investigation_{incident_id}.md',
            'filetype': 'markdown'
        }
        response = requests.post('https://slack.com/api/files.upload', headers=headers, data=data, files=files)
        if response.status_code == 200 and response.json().get('ok'):
            file_url = response.json().get('file', {}).get('permalink', '#')
            file_urls.append(f'🇺🇸 <{file_url}|NA Cluster Analysis>')
            print('✅ NA investigation uploaded')

    # Upload EU results
    if eu_results:
        eu_report = f"""# EU Production Investigation
        
        **Incident:** {incident_id} - {incident_title}
        **Generated:** {timestamp}
        **Region:** Europe (EU)
        ## Investigation Results

        {eu_results}
        """

        files = {
            'file': (f'eu_investigation_{incident_id}.md', eu_report.encode('utf-8'), 'text/markdown')
        }
        data = {
            'channels': channel,
            'title': f'EU Investigation - {incident_title}',
            'filename': f'eu_investigation_{incident_id}.md',
            'filetype': 'markdown'
        }
        response = requests.post('https://slack.com/api/files.upload', headers=headers, data=data, files=files)
        if response.status_code == 200 and response.json().get('ok'):
            file_url = response.json().get('file', {}).get('permalink', '#')
            file_urls.append(f'🇪🇺 <{file_url}|EU Cluster Analysis>')
            print('✅ EU investigation uploaded')

    # Post summary message
    files_section = '\n'.join(file_urls) if file_urls else 'No files uploaded'

    from models.messages import InvestigationResultsMessage
    msg = InvestigationResultsMessage(
        channel=channel,
        incident_id=incident_id,
        incident_title=incident_title,
        incident_severity=incident_severity,
        severity_emoji=severity_emoji,
        affected_services=affected_services,
        tldr_summary=tldr_summary,
        files_section=files_section,
        timestamp=timestamp
    )
    payload = msg.to_message().to_dict()


    response = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=payload)

    if response.status_code == 200 and response.json().get('ok'):
        print('✅ Summary message posted successfully')
    else:
        print(f'❌ Failed to post summary: {response.text}')


if __name__ == '__main__':
    main()