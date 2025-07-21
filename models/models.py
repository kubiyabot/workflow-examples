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
    def get_message(self) -> Message:
        """Generate the command string."""
        pass

class PromptModel(BaseModel, abc.ABC):
    """Base model for prompt generation."""

    @abc.abstractmethod
    def get_prompt(self) -> None:
        """Generate the prompts."""
        pass

class FiletModel(BaseModel, abc.ABC):
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
        return  f"""
                echo "🔍 VALIDATING INCIDENT PARAMETERS"
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
                fi
        """


class ValidationFailure(CommandModel, MessageModel):
    incident_id: str
    incident_title: str
    incident_severity: str
    channel: str
    affected_services: str
    slack_token: str
    output_file: str = "/tmp/validation_agent.json"


    def get_command(self) -> str:
        """Generate shell script to handle validation failure."""

        # Build a message
        msg = self.get_message()
        # Convert message to JSON
        msg_json = msg.to_json()

        return f"""
                echo "🔍 DEBUG: handle-validation-failure step starting"
                echo "affected_services value: {self.affected_services}"
                if [ -n "{self.affected_services}" ]; then
                  echo "🚫 SKIPPING: affected_services is provided - handle-validation-failure will not run"
                  echo "This step only runs when affected_services is missing"
                  exit 0
                fi
                echo "🚨 VALIDATION FAILED - CREATING SERVICE VALIDATION AGENT"
                echo "Affected services is missing, creating agent to help with validation"
                echo "🤖 AGENT CONFIGURATION:"
                echo "Agent Name: incident-service-validator-{self.incident_id}"
                echo "Tools Available: 5 tools"
                echo "- kubectl_get_services: List all cluster services"
                echo "- validate_service_exists: Validate specific services"
                echo "- kubectl_cluster_investigation: Comprehensive cluster analysis"
                echo "- helm_deployments_check: Check recent deployments"
                echo "- workflow_retrigger: Re-trigger workflow with validated services"
                echo ""
                echo "💬 AGENT INSTRUCTIONS:"
                echo "The agent will help users:"
                echo "1. Discover available Kubernetes services"
                echo "2. Validate specific service names"
                echo "3. Re-trigger the workflow with validated services"
                echo ""
                echo "Posting agent notification to channel: {self.channel}"
                echo "📤 Sending Slack message to {self.channel}"
                SLACK_TOKEN=$(echo '{self.slack_token}' | jq -r '.token')

                cat > {self.output_file} << 'EOF'
                    {msg_json}
                EOF

                curl -s -X POST https://slack.com/api/chat.postMessage\\
                  -H "Content-type: application/json" \\
                  -H "Authorization: Bearer $SLACK_TOKEN" \\
                  -d @{self.output_file}

                echo "✅ Service validation agent notification sent to Slack"
            """

    def get_message(self) -> Message:
        from models.messages import ValidationFailureMessage
        return ValidationFailureMessage(
            incident_title=self.incident_title,
            incident_id=self.incident_id,
            incident_severity=self.incident_severity,
            channel=self.channel
        ).to_message()


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
    datadog_metrics_config: str
    observe_supported_ds_ids: str

    def get_prompt(self) -> None:
        """Generate all context prompts based on incident data."""
        self.copilot_prompt = (
            f"INCIDENT TRIAGE SESSION - I am ready to help investigate incident {self.incident_id}: "
            f"{self.incident_title}. Severity: {self.incident_severity}. "
            f"Affected services: {self.affected_services}."
            f"I have access to kubectl, monitoring tools, and can help with investigation commands. "
            f"What would you like to investigate first?"
        )

        self.deep_dive_prompt = (
            f"DEEP DIVE ANALYSIS - Analyzing incident {self.incident_id}: {self.incident_title}. "
            f"Affected services: {self.affected_services}"
            f"I will perform deep analysis using Datadog metrics: {self.datadog_metrics_config} and Observe datasets: {self.observe_supported_ds_ids}. "
            f"I'll focus on root cause analysis, performance metrics, and provide detailed recommendations."
        )

        self.apply_fixes_prompt = (
            f"APPLY FIXES - Ready to apply remediation for incident {self.incident_id}: {self.incident_title}. "
            f"Affected services: {self.affected_services}. "
            f"I have reviewed the investigation findings and will help apply fixes. "
            f"Please confirm which fixes you'd like me to apply or provide specific remediation instructions."
        )

        self.monitoring_prompt = (
            f"MONITORING RECOVERY - Tracking recovery for incident {self.incident_id}: {self.incident_title}. "
            f"Services: {self.affected_services}. "
            f"I will monitor service health, check metrics, and verify that applied fixes are working correctly."
        )


class CopilotContext(CommandModel):
    """Model for preparing context prompts for AI agents."""
    incident_id: str
    incident_title: str
    incident_severity: str
    affected_services: str
    incident_priority: str
    incident_owner: str
    incident_source: str
    customer_impact: str
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


        return f'''
                echo "🔍 PREPARING COPILOT CONTEXT PROMPTS"
                echo "=================================="
                    COPILOT_PROMPT={copilot_prompt}
                    DEEP_DIVE_PROMPT={deep_dive_prompt}
                    APPLY_FIXES_PROMPT={apply_fixes_prompt}
                    MONITORING_PROMPT={monitoring_prompt}
                echo "COPILOT_PROMPT=${{COPILOT_PROMPT}}"
                echo "DEEP_DIVE_PROMPT=${{DEEP_DIVE_PROMPT}}"
                echo "APPLY_FIXES_PROMPT=${{APPLY_FIXES_PROMPT}}"
                echo "MONITORING_PROMPT=${{MONITORING_PROMPT}}"
                echo "✅ Copilot context prompts prepared successfully"
            '''

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
    agent_uuid: str
    copilot_prompt: str = ""
    slack_token: str = ""
    output_file: str = "/tmp/incident_alert.json"

    def get_command(self) -> str:
        copilot_prompt_fallback = (
            f"INCIDENT TRIAGE SESSION - I am ready to help investigate incident {self.incident_id}: "
            f"{self.incident_title}. Severity: {self.incident_severity}. "
            f"Affected services: {self.affected_services}. "
            f"I have access to kubectl, monitoring tools, and can help with investigation commands. "
            f"What would you like to investigate first?"
        )

        copilot_prompt = self.copilot_prompt or copilot_prompt_fallback
        message_json = self.get_message(copilot_prompt).to_json()

        return f'''
            echo "🔍 DEBUG: post-incident-alert step starting";
            echo "affected_services value: {self.affected_services}";
            echo "🚨 POSTING BEAUTIFUL INCIDENT ALERT";
            echo "affected_services provided: {self.affected_services if self.affected_services else 'Not specified'}";
            echo "Posting to channel: {self.channel}";
            echo "Sending beautiful incident alert with blocks...";
            
            COPILOT_PROMPT_FALLBACK="{copilot_prompt_fallback}";
            COPILOT_PROMPT_VALUE="{copilot_prompt}";
            
            echo "DEBUG: Using copilot prompt: $COPILOT_PROMPT_VALUE";
            cat > {self.output_file} << 'EOF'
                {message_json}
            EOF
            
            echo "DEBUG: slack_token.token is: '{self.slack_token}'";    
            
            RESPONSE=$(curl -s -X POST https://slack.com/api/chat.postMessage 
                -H "Authorization: Bearer {self.slack_token}"
                -H "Content-Type: application/json" 
                -d @/tmp/incident_alert.json
            );
            
            echo "Slack API response: $RESPONSE";
            
            if [ $? -eq 0 ]; then 
                echo "✅ Slack message posted successfully"; 
            else 
                echo "❌ Failed to post Slack message"; 
                echo "DEBUG: curl exit code: $?"; exit 1; 
            fi;
            
            echo "✅ Beautiful incident alert posted to Slack"
        '''

    def get_message(self, copilot_prompt: str) -> Message:
        from models.messages import PostIncidentAlertMessage

        return PostIncidentAlertMessage(
            incident_title=self.incident_title,
            incident_id=self.incident_id,
            incident_severity=self.incident_severity,
            incident_priority=self.incident_priority,
            affected_services=self.affected_services,
            incident_body=self.incident_body,
            incident_url=self.incident_url,
            agent_uuid=self.agent_uuid,
            channel=self.channel,
            copilot_prompt=copilot_prompt
        ).to_message()


class InvestigationStart(CommandModel, MessageModel):
    channel: str
    investigation_agent: str
    investigation_timeout: str
    affected_services: str
    max_retries: str
    slack_token: str
    output_file: str = "/tmp/investigation_start.json"

    def get_command(self) -> str:
        msg = self.get_message()
        json_data = msg.to_json()

        return f'''
            echo "🔍 DEBUG: notify-investigation-start step starting"
            echo "affected_services value: {self.affected_services}"
            echo "🔍 NOTIFYING INVESTIGATION START"
            echo "affected_services provided: ${{affected_services:-Not specified}}"
            echo "Posting to channel: {self.channel}"
            echo "Sending beautiful investigation start notification..."
            
            cat > {self.output_file} << 'EOF'
                {json_data}
            EOF
            
            curl -s -X POST https://slack.com/api/chat.postMessage \
                -H "Authorization: Bearer {self.slack_token}" \
                -H "Content-Type: application/json" \
                -d @{self.output_file}
            echo "✅ Beautiful investigation start notification posted to Slack"
        '''

    def get_message(self) -> Message:
        from models.messages import InvestigationStartMessage
        return InvestigationStartMessage(
            channel=self.channel,
            investigation_agent=self.investigation_agent,
            investigation_timeout=self.investigation_timeout,
            max_retries=self.max_retries
        ).to_message()

class InvestigateKubernetesClusterHealth(CommandModel):
    """Model for investigating Kubernetes cluster health."""
    incident_id: str
    incident_title: str
    incident_severity: str
    datadog_metrics_config: str

    def get_command(self) -> str:
        return f"""You are running in AUTOMATION MODE with NO USER INTERACTION capabilities. Generate a STRUCTURED TECHNICAL REPORT following this exact format:

            # CLUSTER HEALTH INVESTIGATION
    
            ## EXECUTIVE SUMMARY
            Provide a 2-3 sentence overview of the cluster state and any critical issues found.
    
            ## INVESTIGATION SCOPE
            - Incident: {self.incident_id} - {self.incident_title}
            - Severity: {self.incident_severity}
            - Investigation Focus: Cluster-wide health assessment
    
            ## FINDINGS
    
            ### 1. NGINX Ingress Controller Status
            [Provide detailed findings with commands and outputs]
    
            ### 2. Service Health & Endpoints
            [Provide detailed findings with commands and outputs]
    
            ### 3. Kube-Proxy DaemonSet Status
            [Provide detailed findings with commands and outputs]
    
            ### 4. Kong API Gateway Analysis
            [Provide detailed findings with commands and outputs]
    
            ### 5. Node Health & Resource Pressure
            [Provide detailed findings with commands and outputs]
    
            ### 6. Kube-System Components
            [Provide detailed findings with commands and outputs]
    
            ## CRITICAL OBSERVATIONS
            - List key issues found
            - Include error patterns
            - Note resource constraints
    
            ## METRICS ANALYSIS
            IMPORTANT: Use ONLY these Datadog metrics: {self.datadog_metrics_config}
            [Provide metric analysis results]
    
            ## COMMANDS EXECUTED
    
            ```bash
            # List all commands executed during investigation
            ```
    
            ## RECOMMENDATIONS
            1. [Immediate actions needed]
            2. [Short-term fixes]
            3. [Long-term improvements]
    
            IMPORTANT: End your report with:
            SUMMARY_FOR_SLACK: [3-5 line summary using only alphanumeric characters, spaces, periods, commas, and hyphens]"""



class InvestigateServiceSpecific(CommandModel):
    """Model for investigating Kubernetes cluster health."""
    incident_id: str
    incident_title: str
    incident_severity: str
    affected_services: str
    k8s_environment: str
    observe_supported_ds_ids: str
    dd_environment: str
    datadog_metrics_config: str

    def get_command(self) -> str:
        return f"""You are running in AUTOMATION MODE with NO USER INTERACTION capabilities. Generate a STRUCTURED TECHNICAL REPORT following this exact format:

            # SERVICE-SPECIFIC INVESTIGATION
            
            ## EXECUTIVE SUMMARY
            Provide a 2-3 sentence overview of the service state and root cause if identified.
            
            ## INVESTIGATION SCOPE
            - Incident: {self.incident_id} - {self.incident_title}
            - Affected Services: {self.affected_services}
            - Target Namespace: {self.k8s_environment}
            - Severity: {self.incident_severity}
            
            ## SERVICE ANALYSIS
            
            ### 1. Pod Health Status
            [Detail unhealthy pods, restart counts, and failure reasons]
            
            ### 2. Application Logs Analysis
            [Key error patterns and timestamps from the last hour]
            Datasets analyzed: {self.observe_supported_ds_ids}
            
            ### 3. Events & Alerts
            [Recent Kubernetes events and triggered alerts]
            
            ### 4. Resource Utilization
            [CPU, Memory, and other resource metrics]
            
            ### 5. Networking & Connectivity
            [Service endpoints, ingress rules, and connectivity issues]
            
            ## APM ANALYSIS (Environment: {self.dd_environment})
            
            ### Error Analysis
            [Error rates, types, and patterns]
            
            ### Latency Metrics
            [Response times and performance degradation]
            
            ### Trace Analysis
            [Critical path analysis and bottlenecks]
            
            ## ROOT CAUSE ANALYSIS
            
            ### Identified Issues
            1. [Primary root cause if identified]
            2. [Contributing factors]
            3. [Cascade effects]
            
            ### Timeline of Events
            - [Time]: [Event description]
            - [Time]: [Event description]
            
            ## METRICS DEEP DIVE
            IMPORTANT: Using ONLY these Datadog metrics: {self.datadog_metrics_config}
            [Provide detailed metric analysis]
            
            ## COMMANDS EXECUTED
            ```bash
            # List all commands executed during investigation
            ```
            
            ## REMEDIATION PLAN
            
            ### Immediate Actions
            1. [Step-by-step immediate fixes]
            2. [Commands to execute]
            
            ### Validation Steps
            1. [How to verify fixes]
            2. [Expected outcomes]
            
            ### Prevention Measures
            1. [Long-term fixes]
            2. [Monitoring improvements]
            
            IMPORTANT: End your report with:
            SUMMARY_FOR_SLACK: [3-5 line summary using only alphanumeric characters, spaces, periods, commas, and hyphens]"""


class IncidentReportData(PromptModel):
    incident_id: str
    incident_title: str
    incident_severity: str
    affected_services: str
    cleaned_cluster_results: str
    cleaned_service_results: str

    system_prompt: str = ""
    prompt: str = ""


    def get_prompt(self):
        self.system_prompt = """
            You are a technical writer creating an EXECUTIVE INCIDENT REPORT. 
            You will receive cleaned investigation data and must create a well-formatted document suitable for 
            both executive stakeholders and technical teams.
        """

        self.prompt = f"""
            Create a comprehensive incident report that starts with a clear TLDR section, followed by the technical details.

            ## INPUT DATA
            - Incident ID: {self.incident_id}
            - Title: {self.incident_title}
            - Severity: {self.incident_severity}
            - Affected Services: {self.affected_services}
            - Cluster Investigation Results: {self.cleaned_cluster_results}
            - Service Investigation Results: {self.cleaned_service_results}
            
            ## REQUIRED OUTPUT FORMAT
            
            # 🚨 INCIDENT REPORT: {self.incident_title}
            
            ## 📋 TLDR - EXECUTIVE SUMMARY
            
            ### 🎯 Key Findings
            - **Root Cause**: [Identified root cause in one sentence]
            - **Impact**: [Business/customer impact in one sentence]
            - **Current Status**: [Current state and any ongoing issues]
            - **Resolution Time**: [Estimated or actual resolution time]
            
            ### 🔍 Quick Facts
            | Metric | Value |
            |--------|-------|
            | Incident ID | {self.incident_id} |
            | Severity | {self.incident_severity} |
            | Affected Services | {self.affected_services} |
            | Investigation Started | [Time] |
            | Primary Issue | [One line description] |
            
            ### ⚡ Immediate Actions Required
            1. [Most critical action]
            2. [Second priority action]
            3. [Third priority action]
            
            ### 📊 Impact Assessment
            - **Service Availability**: [e.g., 85% degraded, 15% down]
            - **Customer Impact**: [e.g., High - affecting production workloads]
            - **Data Loss Risk**: [e.g., None identified]
            - **Security Impact**: [e.g., No security implications]
            
            ---
            
            ## 🔬 TECHNICAL INVESTIGATION DETAILS
            
            ### Cluster-Wide Health Analysis
            [Insert formatted summary from cluster investigation]
            
            ### Service-Specific Analysis
            [Insert formatted summary from service investigation]
            
            ### Root Cause Deep Dive
            [Synthesize the root cause findings from both reports]
            
            ### Timeline of Events
            [Create a merged timeline from both investigations]
            
            ---
            
            ## 💡 RECOMMENDATIONS
            
            ### Immediate Remediation
            [Prioritized list of immediate fixes from both reports]
            
            ### Short-term Improvements
            [Actions to prevent recurrence in the next 30 days]
            
            ### Long-term Strategy
            [Strategic improvements for system resilience]
            
            ---
            
            ## 📈 METRICS & MONITORING
            
            ### Key Metrics Observed
            [Summary of critical metrics from both investigations]
            
            ### Monitoring Gaps Identified
            [What monitoring improvements are needed]
            
            ---
            
            ## ✅ NEXT STEPS
            1. [Action item with owner]
            2. [Action item with owner]
            3. [Action item with owner]
            
            ---
            
            
            _Report generated at: [timestamp]_
            
            _Investigation conducted by: AI Investigation Agent_
            
            IMPORTANT: Your output should be clean markdown suitable for Slack upload. Focus on clarity, actionability, 
            and proper formatting. Extract and highlight the most critical information from the technical reports while maintaining accuracy.
        """
        return self


class ExecutiveSummaryData(PromptModel):
    incident_id: str
    incident_title: str
    incident_severity: str
    affected_services: str
    formatted_incident_report: str

    system_prompt: str = ""
    prompt: str = ""

    def get_prompt(self):
        self.system_prompt = """
            You are an expert at creating concise executive summaries for technical incident reports. 
            Focus on business impact, root causes, and actionable items. Remove all technical commands, verbose logs, and implementation details.
        """

        self.prompt = f"""
            Create a concise executive summary for this incident investigation. Return a JSON object with the following structure:
    
            {{
              "tldr": "2-3 sentence executive summary highlighting the root cause, impact, and resolution status",
              "key_findings": [
                "Finding 1 - concise and business-focused",
                "Finding 2 - concise and business-focused",
                "Finding 3 - concise and business-focused"
              ],
              "root_cause": "One sentence explaining the root cause in business terms",
              "business_impact": "One sentence describing customer/business impact",
              "immediate_actions": [
                "Action 1 - what needs to be done now",
                "Action 2 - what needs to be done now"
              ],
              "slack_summary": "3-5 line summary for Slack message using plain language",
              "incident_status": "Current status: Active/Mitigated/Resolved",
              "estimated_resolution": "Timeframe for full resolution"
            }}
            
            Incident Details:
            - ID: {self.incident_id}
            - Title: {self.incident_title}
            - Severity: {self.incident_severity}
            - Affected Services: {self.affected_services}
            
            Full Investigation Report:
                {self.formatted_incident_report}
            
            Focus on clarity, brevity, and actionability. Avoid technical jargon where possible.
        """
        return self


class CleanClusterInvestigationData(PromptModel):
    kubernetes_cluster_health_results: str

    system_prompt: str = ""
    prompt: str = ""

    def get_prompt(self):
        self.system_prompt = """
            You are a data cleaning expert. Your job is to extract ONLY the actual investigation results from raw agent output, 
            removing all CLI formatting, connection messages, and execution details.
        """

        self.prompt = f"""
            Extract ONLY the actual investigation findings from this raw output. Remove ALL:
            - Connection messages (e.g., '🔗 Connecting to agent runner service')
            - CLI formatting (e.g., '🚀 EXECUTING kubectl')
            - Execution details (e.g., '📋 Parameters:', '⏳ Initializing')
            - Progress indicators
            - Empty outputs (e.g., '│ kubectl │ ""')
            
            Return ONLY the actual technical findings and analysis content that was generated by the investigation agent.
            
            Raw Output:
            {self.kubernetes_cluster_health_results}
        """
        return self


class CleanServiceInvestigationData(PromptModel):
    service_specific_results: str

    system_prompt: str = ""
    prompt: str = ""

    def get_prompt(self):
        self.system_prompt = """
            You are a data cleaning expert. Your job is to extract ONLY the actual investigation results from raw agent output, 
            removing all CLI formatting, connection messages, and execution details.
        """

        self.prompt = f"""
            Extract ONLY the actual investigation findings from this raw output. Remove ALL:
            - Connection messages (e.g., '🔗 Connecting to agent runner service')
            - CLI formatting (e.g., '🚀 EXECUTING kubectl')
            - Execution details (e.g., '📋 Parameters:', '⏳ Initializing')
            - Progress indicators
            - Empty outputs (e.g., '│ kubectl │ ""')
            
            Return ONLY the actual technical findings and analysis content that was generated by the investigation agent.
    
            Raw Output:
            {self.service_specific_results}
        """
        return self


class FormatSlackReportsData(PromptModel):
    cleaned_cluster_results: str
    cleaned_service_results: str

    system_prompt: str = ""
    prompt: str = ""

    def get_prompt(self):
        self.system_prompt = """
            You are creating concise technical summaries for incident reports. Focus on key findings, metrics, and actionable insights. 
            The input has already been cleaned of CLI formatting.
        """

        self.prompt = f"""
            Create concise versions of the technical investigation reports suitable for executive review. Format as clean markdown.
    
            # TASK 1: Summarize Cluster Health Investigation
            Create a concise summary (max 500 words) focusing on:
            - Overall cluster health status
            - Critical issues found
            - Key metrics and their implications
            - Recommended actions
            
            Cluster Investigation Results:
            {self.cleaned_cluster_results}
            
            ---
            
            # TASK 2: Summarize Service-Specific Investigation
            Create a concise summary (max 500 words) focusing on:
            - Service health and availability
            - Root cause indicators
            - Performance metrics
            - Immediate remediation steps
            
            Service Investigation Results:
            {self.cleaned_service_results}
            
            ---
            
            Return the summaries in this format:
            
            ## CLUSTER_HEALTH_SUMMARY
            [Your concise cluster summary here]
            
            ## SERVICE_INVESTIGATION_SUMMARY
            [Your concise service summary here]
            
            Use bullet points, clear headings, and focus on actionable insights.
        """
        return self


class InvestigationResults(CommandModel, FiletModel):
    input_file: str
    output_file: str

    def get_command(self) -> str:
        return f"pip install requests && python {self.output_file}"

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
