import abc

from pydantic import BaseModel
from typing import Union, List, Dict

from models.messages import Message

class CommandModel(BaseModel, abc.ABC):
    """Base model for command generation."""

    @abc.abstractmethod
    def get_command(self) -> str:
        """Generate the command string."""
        pass

class MessageModel(BaseModel, abc.ABC):
    """Base model for command generation."""

    @abc.abstractmethod
    def get_message(self, **kwargs) -> Message:
        """Generate the command string."""
        pass

class PromptModel(BaseModel, abc.ABC):
    """Base model for prompt generation."""

    @abc.abstractmethod
    def get_prompt(self) -> None:
        """Generate the prompts."""
        pass

class FileModel(BaseModel, abc.ABC):
    """Base model for prompt generation."""

    @abc.abstractmethod
    def get_files(self) -> None:
        """Generate the prompts."""
        pass


class ValidateIncident(CommandModel):
    """Model for validating incidents."""
    incident_id: str
    incident_title: str
    incident_severity: str
    affected_services: str
    incident_priority: str
    incident_owner: str
    incident_source: str
    customer_impact: str

    def get_command(self) -> str:
        return  f"""echo "🔍 VALIDATING INCIDENT PARAMETERS"
                echo "================================="
                VALIDATION_PASSED=true
                MISSING_PARAMS=""
                if [ -z "{self.incident_id}" ]; then
                  echo "❌ ERROR: incident_id is required"
                  VALIDATION_PASSED=false
                  MISSING_PARAMS="${{MISSING_PARAMS}} incident_id"
                fi
                if [ -z "{self.incident_title}" ]; then
                  echo "❌ ERROR: incident_title is required"
                  VALIDATION_PASSED=false
                  MISSING_PARAMS="${{MISSING_PARAMS}} incident_title"
                fi
                if [ -z "{self.incident_severity}" ]; then
                  echo "❌ ERROR: incident_severity is required"
                  VALIDATION_PASSED=false
                  MISSING_PARAMS="${{MISSING_PARAMS}} incident_severity"
                fi
                if [ -z "{self.affected_services}" ]; then
                  echo "⚠️ WARNING: affected_services not provided - will create validation agent"
                fi
                case "{self.incident_severity}" in
                  "critical"|"high"|"medium"|"low")
                    echo "✅ Severity {self.incident_severity} is valid"
                    ;;
                  *)
                    echo "❌ ERROR: Invalid severity {self.incident_severity}. Must be: critical, high, medium, or low"
                    VALIDATION_PASSED=false
                    MISSING_PARAMS="${{MISSING_PARAMS}} valid_severity"
                    ;;
                esac
                if [ "$VALIDATION_PASSED" = "true" ]; then
                  echo "📋 INCIDENT METADATA:"
                  echo "  ID: {self.incident_id}"
                  echo "  Title: {self.incident_title}"
                  echo "  Severity: {self.incident_severity}"
                  echo "  Priority: {self.incident_priority}"
                  echo "  Owner: {self.incident_owner}"
                  echo "  Source: {self.incident_source}"
                  echo "  Affected Services: ${{affected_services:-TBD via agent}}"
                  echo "  Customer Impact: {self.customer_impact}"
                  echo ""
                  echo "✅ Incident validation completed successfully"
                else
                  echo "❌ Validation failed. Missing parameters: ${{MISSING_PARAMS}}"
                  echo "⚠️ Continuing workflow to handle validation failure..."
                fi"""


class ValidationFailure(CommandModel):
    missing_params: str

    def get_command(self) -> str:
        """Generate shell script to handle validation failure."""
        return f"""
            if [ "$VALIDATION_PASSED" != "true" ]; then 
                echo "⚠️ VALIDATION FAILURE DETECTED: Creating support agent to help"; 
                echo "Missing required parameters: {self.missing_params}"; 
                echo "Will create an intelligent agent to assist with parameter collection"; 
            else 
                echo "✅ All required parameters present"; 
            fi
        """


class SupportedDatasets(CommandModel):
    datasets: Union[List[str], str] = None

    def get_command(self) -> str:
        """Generate shell script to retrieve supported dataset item."""

        if self.datasets is None:
            self.datasets = [
                "api-logs",
                "server-logs",
                "application-logs",
                "error-logs",
                "trace-logs",
                "audit-logs",
                "security-logs",
                "performance-logs"
            ]
        if isinstance(self.datasets, list):
            self.datasets = ",".join(self.datasets)

        return f"""
                echo "📊 FETCHING OBSERVE SUPPORTED DATASET IDS"
                echo "=========================================="
                SUPPORTED_DATASETS='{self.datasets}'
                echo "Available Dataset IDs for Observe: $SUPPORTED_DATASETS"
                echo "✅ Observe supported dataset IDs retrieved successfully"
            """

class DatadogMetrics(CommandModel):
    metrics: Union[List[str], str] = None

    def get_command(self) -> str:
        """Generate shell script to retrieve supported datadog metrics config."""

        if self.metrics is None:
            self.metrics = [
                "system.cpu.usage",
                "system.memory.usage",
                "kubernetes.cpu.usage",
                "kubernetes.memory.usage",
                "kubernetes.pods.running",
                "kubernetes.pods.failed",
                "nginx.requests.rate",
                "nginx.response.time",
                "kong.requests.rate",
                "kong.response.time",
                "kong.errors.rate",
                "application.response.time",
                "application.error.rate",
                "application.throughput",
                "jvm.heap.usage",
                "jvm.gc.time",
                "trace.servlet.request.errors",
                "trace.servlet.request.hits",
                "trace.servlet.request"
            ]
        if isinstance(self.metrics, list):
            self.metrics = ",".join(self.metrics)

        return f"""
                echo "�? FETCHING DATADOG METRICS CONFIGURATION"
                echo "========================================="
                DD_METRICS='{self.metrics}'
                echo "Available Datadog Metrics: $DD_METRICS"
                echo "✅ Datadog metrics configuration retrieved successfully"
            """


class CopilotContextData(PromptModel):
    """Data model for copilot context prompts."""
    incident_id: str
    incident_title: str
    incident_severity: str
    affected_services: str
    copilot_prompt: str = ""
    deep_dive_prompt: str = ""
    apply_fixes_prompt: str = ""
    monitoring_prompt: str = ""
    na_followup_prompt: str = ""
    eu_followup_prompt: str = ""
    datadog_metrics_config: str
    observe_supported_ds_ids: str

    def get_prompt(self) -> None:
        """Generate all context prompts based on incident data."""
        self.copilot_prompt = (
            f"You are an INCIDENT RESPONDER AGENT with access to kubectl, Datadog, and Observe. "
            f"INCIDENT CONTEXT: ID={self.incident_id}, Title='{self.incident_title}', Severity={self.incident_severity}, Services={self.affected_services}. "
            f"I will now gather relevant logs and metrics from: Datadog metrics ({self.datadog_metrics_config}) and Observe datasets ({self.observe_supported_ds_ids}). "
            f"Please wait while I collect this data... Once complete, I'll ask what specific aspect you'd like to investigate. "
        )

        self.deep_dive_prompt = (
            f"You are an INCIDENT RESPONDER AGENT performing deep analysis. "
            f"INCIDENT: {self.incident_id} - {self.incident_title}. "
            f"I'm gathering comprehensive data from Datadog metrics: {self.datadog_metrics_config} and Observe datasets: {self.observe_supported_ds_ids}. "
            f"Analyzing affected services: {self.affected_services}. "
            f"I'll provide root cause analysis, performance metrics, and actionable recommendations. Collecting data now..."
        )

        self.apply_fixes_prompt = (
            f"You are an INCIDENT RESPONDER AGENT ready to apply remediation. "
            f"INCIDENT: {self.incident_id} - {self.incident_title}. Services: {self.affected_services}. "
            f"I have access to kubectl for applying fixes. Let me review the investigation findings first... "
            f"Once ready, I'll present the available fixes and ask which ones you'd like me to apply."
        )

        self.monitoring_prompt = (
            f"You are an INCIDENT RESPONDER AGENT monitoring recovery. "
            f"INCIDENT: {self.incident_id} - {self.incident_title}. Services: {self.affected_services}. "
            f"I'm tracking recovery using Datadog metrics: {self.datadog_metrics_config}. "
            f"Let me check current service health and metrics... I'll then provide status updates and verify applied fixes."
        )

        self.na_followup_prompt = (
            f"You are an INCIDENT RESPONDER AGENT focusing on NA PRODUCTION. "
            f"INCIDENT: {self.incident_id} - {self.incident_title}. Region: North America. "
            f"I have access to kubectl (NA cluster), Datadog metrics: {self.datadog_metrics_config}, and Observe datasets: {self.observe_supported_ds_ids}. "
            f"Let me gather NA-specific logs and metrics first... What aspect of the NA cluster would you like me to investigate?"
        )

        self.eu_followup_prompt = (
            f"You are an INCIDENT RESPONDER AGENT focusing on EU PRODUCTION. "
            f"INCIDENT: {self.incident_id} - {self.incident_title}. Region: Europe. "
            f"I have access to kubectl (EU cluster), Datadog metrics: {self.datadog_metrics_config}, and Observe datasets: {self.observe_supported_ds_ids}. "
            f"Let me gather NA-specific logs and metrics first... What aspect of the NA cluster would you like me to investigate?"
        )



class CopilotContext(CommandModel):
    """Model for preparing context prompts for AI agents."""
    incident_id: str
    incident_title: str
    incident_severity: str
    affected_services: str
    incident_priority: str
    datadog_metrics_config: str
    observe_supported_ds_ids: str

    def get_command(self) -> str:
        # Create copilot context data and generate prompts
        context_data = CopilotContextData(
            incident_id=self.incident_id,
            incident_title=self.incident_title,
            incident_severity=self.incident_severity,
            affected_services=self.affected_services,
            datadog_metrics_config=self.datadog_metrics_config,
            observe_supported_ds_ids=self.observe_supported_ds_ids
        )
        context_data.get_prompt()

        copilot_prompt = context_data.copilot_prompt
        deep_dive_prompt = context_data.deep_dive_prompt
        apply_fixes_prompt = context_data.apply_fixes_prompt
        monitoring_prompt = context_data.monitoring_prompt
        na_followup_prompt = context_data.na_followup_prompt
        eu_followup_prompt = context_data.eu_followup_prompt

        return (
            f'echo "🔍 PREPARING COPILOT CONTEXT PROMPTS";\n'
            f'echo "==================================";\n'
            f'COPILOT_PROMPT="{copilot_prompt}";\n'
            f'DEEP_DIVE_PROMPT="{deep_dive_prompt}";\n'
            f'APPLY_FIXES_PROMPT="{apply_fixes_prompt}";\n'
            f'MONITORING_PROMPT="{monitoring_prompt}";\n'
            f'NA_FOLLOWUP_PROMPT="{na_followup_prompt}";\n'
            f'EU_FOLLOWUP_PROMPT="{eu_followup_prompt}";\n'
            f'echo "COPILOT_PROMPT=${{COPILOT_PROMPT}}";\n'
            f'echo "DEEP_DIVE_PROMPT=${{DEEP_DIVE_PROMPT}}";\n'
            f'echo "APPLY_FIXES_PROMPT=${{APPLY_FIXES_PROMPT}}";\n'
            f'echo "MONITORING_PROMPT=${{MONITORING_PROMPT}}";\n'
            f'echo "NA_FOLLOWUP_PROMPT=${{NA_FOLLOWUP_PROMPT}}";\n'
            f'echo "EU_FOLLOWUP_PROMPT=${{EU_FOLLOWUP_PROMPT}}";\n'
            f'echo "✅ Copilot context prompts prepared successfully"'
        )


class NormalizeChannelNameCommand(CommandModel):
    """Model for normalizing Slack channel names."""
    slack_channel_id: str
    normalize_channel_name: str

    def get_command(self) -> str:
        return (
            f'if [ "{self.normalize_channel_name}" = "true" ]; then '
            f'echo "{self.slack_channel_id}" | sed \'s/ /_/g\' | tr \'[:upper:]\' \'[:lower:]\'; '
            f'else echo "{self.slack_channel_id}"; fi'
        )


class PostIncidentAlert(CommandModel, MessageModel):
    """Model for posting a beautiful incident alert to Slack."""
    incident_id: str
    incident_title: str
    incident_severity: str
    incident_priority: str
    affected_services: str
    incident_body: str
    incident_url: str
    channel: str
    slack_token: str = ""
    output_file: str = "/tmp/incident_alert.json"

    def get_command(self) -> str:
        msg = self.get_message()
        msg_json = msg.to_json()

        return f"""echo "🚨 POSTING INCIDENT ALERT"
            echo "Posting to channel: ${{NORMALIZED_CHANNEL_NAME}}"
            SEVERITY_EMOJI=""
            case "{self.incident_severity}" in
                critical) SEVERITY_EMOJI="🔴" ;;
                high) SEVERITY_EMOJI="🟠" ;;
                medium) SEVERITY_EMOJI="🟡" ;;
                low) SEVERITY_EMOJI="🟢" ;;
                *) SEVERITY_EMOJI="⚪" ;;
            esac
            echo "{msg_json}" > {self.output_file}
            RESPONSE=$(curl -s -X POST https://slack.com/api/chat.postMessage
                -H "Authorization: Bearer {self.slack_token}"
                -H "Content-Type: application/json"
                -d @{self.output_file}
            )
            echo "Slack API response: $RESPONSE"
            if [ $? -eq 0 ]; then
                echo "✅ Incident alert posted successfully"
            else
                echo "❌ Failed to post incident alert"
                exit 1
            fi"""

        # another way by using only python
        """
            import os
            channel_name = os.getenv("NORMALIZED_CHANNEL_NAME")
            print("🚨 POSTING INCIDENT ALERT")
            print(f"Posting to channel: {channel_name}")
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(self.incident_severity.lower(), '⚪')
            status = self.get_message(severity_emoji=severity_emoji).send(token=self.slack_token)
            if status == 200:
                print("✅ Incident alert posted successfully")
            else:
                print("❌ Failed to post incident alert")
        """


    def get_message(self, **kwargs) -> Message:
        from models.messages import PostIncidentAlertMessage

        return PostIncidentAlertMessage(
            incident_title=self.incident_title,
            incident_id=self.incident_id,
            incident_severity=self.incident_severity,
            severity_emoji=kwargs.get("severity_emoji", "${SEVERITY_EMOJI}"),
            incident_priority=self.incident_priority,
            affected_services=self.affected_services,
            incident_body=self.incident_body,
            incident_url=self.incident_url,
            channel=self.channel,
        ).to_message()


class InvestigationProgress(CommandModel, MessageModel):
    channel: str
    incident_id: str
    incident_title: str
    incident_severity: str
    investigation_timeout: str
    affected_services: str
    slack_token: str
    output_file: str = "/tmp/investigation_progress.json"

    def get_command(self) -> str:
        msg = self.get_message()
        msg_json = msg.to_json()

        return f'''echo "📊 POSTING INVESTIGATION PROGRESS UPDATE"
            echo "Posting to channel: {self.channel}"
            TIMEOUT_SECONDS="{self.investigation_timeout}"
            TIMEOUT_MINUTES=$((TIMEOUT_SECONDS / 60))
            
            echo "{msg_json}" > {self.output_file}
            
            curl -s -X POST https://slack.com/api/chat.postMessage 
                -H "Authorization: Bearer {self.slack_token}" 
                -H "Content-Type: application/json"
                -d @{self.output_file}
            
            echo "✅ Investigation progress notification posted to Slack"'''

    def get_message(self) -> Message:
        from models.messages import InvestigationProgressMessage
        return InvestigationProgressMessage(
            channel=self.channel,
            incident_id=self.incident_id,
            incident_title=self.incident_title,
            incident_severity=self.incident_severity,
            affected_services=self.affected_services,
            timeout_minutes="${TIMEOUT_MINUTES}",
        ).to_message()

class InvestigateNAClusterHealth(CommandModel):
    """Model for investigating Kubernetes cluster health."""
    incident_id: str
    incident_title: str

    def get_command(self) -> str:
        return f"""I need help investigating an incident in the NA Production cluster. The incident ID is {self.incident_id} and title is '{self.incident_title}'. 
            Could you analyze the cluster health including service status, pod health, network connectivity, and recent events? I'd also like to understand any cross-region dependencies.
            Please use kubectl, Datadog metrics, and Observe datasets to gather information.

            IMPORTANT: Please provide ONLY the investigation findings in your response. Do NOT include:
            - Connection status messages
            - Agent initialization messages
            - Tool execution logs
            - Progress indicators

            Just provide a clean, structured report with your findings and recommendations."""

class InvestigateEUClusterHealth(CommandModel):
    """Model for investigating Kubernetes cluster health."""
    incident_id: str
    incident_title: str

    def get_command(self) -> str:
        return f"""I need help investigating an incident in the EU Production cluster. The incident ID is {self.incident_id} and title is '{self.incident_title}' .  
            Could you analyze the cluster health including service status, pod health, network connectivity, and recent events? 
            I'd also like to understand any cross-region dependencies. 
            Please use kubectl, Datadog metrics, and Observe datasets to gather information.
            
            IMPORTANT: Please provide ONLY the investigation findings in your response. Do NOT include:
            - Connection status messages
            - Agent initialization messages
            - Tool execution logs
            - Progress indicators
            
            Just provide a clean, structured report with your findings and recommendations."""

class IncidentReport(CommandModel):
    """Model for investigating Kubernetes cluster health."""
    incident_id: str
    incident_title: str
    incident_severity: str
    affected_services: str
    cleaned_na_results: str
    cleaned_eu_results: str

    def get_command(self) -> str:
        return f"""Create a comprehensive incident report based on the following investigation data:
            
            Incident Details:
            - ID: {self.incident_id}
            - Title: {self.incident_title}
            - Severity: {self.incident_severity}
            - Affected Services: {self.affected_services}
            
            NA Cluster Investigation Results:
            {self.cleaned_na_results}
            
            EU Cluster Investigation Results:
            {self.cleaned_eu_results}
            
            Please create an executive incident report that includes:
            1. Executive Summary (brief overview of the incident and findings)
            2. Key Findings (main issues discovered in both regions)
            3. Root Cause Analysis
            4. Impact Assessment
            5. Immediate Actions Required
            6. Recommended Next Steps
            7. Lessons Learned
            
            Format the report in clean markdown suitable for Slack display."""


class ExecutiveSummary(CommandModel):
    """Model for investigating Kubernetes cluster health."""
    incident_id: str
    incident_title: str
    incident_severity: str
    affected_services: str
    formatted_incident_report: str

    def get_command(self) -> str:
        return f"""Create an executive summary based on the incident investigation.
            
            Incident: {self.incident_id} - {self.incident_title}
            Severity: {self.incident_severity}
            Services: {self.affected_services}
            
            Full Incident Report:
            {self.formatted_incident_report}
            
            Please create a JSON response with this structure:
            {{
              "tldr": "2-3 sentence summary of the incident and key findings",
              "key_findings": ["finding1", "finding2", "finding3"],
              "root_cause": "one sentence describing the root cause",
              "business_impact": "one sentence describing business impact",
              "immediate_actions": ["action1", "action2"],
              "slack_summary": "3-5 line summary for Slack notification",
              "incident_status": "Active/Mitigated/Resolved",
              "estimated_resolution": "timeframe for resolution"
            }}
            
            Base your summary on the incident report provided above."""


class CleanNAInvestigation(CommandModel):
    """Model for cleaning NA cluster investigation results."""
    na_cluster_results: str

    def get_command(self) -> str:
        return f"""Based on the NA cluster investigation results below, please provide a clean summary of the key findings:
        
            {self.na_cluster_results}:
            
            Provide a structured summary with:
            - Key findings (3-5 bullet points)
            - Any issues or anomalies detected
            - Current cluster health status
            - Recommendations if any
            
            Focus only on the technical findings, ignore any CLI output or connection messages."""


class CleanEUInvestigation(CommandModel):
    """Model for cleaning NA cluster investigation results."""
    eu_cluster_results: str

    def get_command(self) -> str:
        return f"""Based on the EU cluster investigation results below, please provide a clean summary of the key findings:

            {self.eu_cluster_results}:

            Provide a structured summary with:
            - Key findings (3-5 bullet points)
            - Any issues or anomalies detected
            - Current cluster health status
            - Recommendations if any

            Focus only on the technical findings, ignore any CLI output or connection messages."""

class FormatSlackReports(CommandModel):
    """Model for cleaning NA cluster investigation results."""
    cleaned_na_results: str
    cleaned_eu_results: str

    def get_command(self) -> str:
        return f"""I need you to create concise technical summaries for an incident report. Here's the investigation data:

            ## NA Cluster Investigation Results:
            {self.cleaned_na_results}
            
            ## EU Cluster Investigation Results:
            {self.cleaned_eu_results}
            
            Please create a cross-region summary that includes:
            1. North America (NA) Production - health status, critical issues, key metrics, recommendations
            2. Europe (EU) Production - health status, critical issues, key metrics, recommendations
            3. Cross-Region Impact Analysis - dependencies, common issues, coordinated remediation approach
            
            Format as clean markdown with bullet points and clear headings."""


class InvestigationResults(CommandModel, FileModel):
    input_file: str
    output_file: str

    def get_command(self) -> str:
        return f"pip install --no-cache-dir requests && python {self.output_file}"

    def get_files(self) -> List[Dict[str, str]]:
        # Read the input_file content as a string
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception as e:
            file_content = f"ERROR: Could not read file {self.input_file}: {e}"
        return [
            {
                "destination": self.output_file,
                "content": file_content
            }
        ]
