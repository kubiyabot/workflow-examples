def generate_incident_response_workflow() -> 'Workflow':

    from kubiya_workflow_sdk.dsl import Workflow
    from models.models import (
        ValidateIncident,
        ValidationFailure,
        SupportedDatasets,
        DatadogMetrics,
        CopilotContext,
        PostIncidentAlert,
        InvestigationStart,
        InvestigateKubernetesClusterHealth,
        InvestigateServiceSpecific,
        IncidentReportData,
        ExecutiveSummaryData,
        CleanClusterInvestigationData,
        CleanServiceInvestigationData,
        FormatSlackReportsData,
        InvestigationResults,
    )
    wf = (
        Workflow("production-incident-workflow")
        .description("Production-grade incident response workflow with AI investigation and Slack integration")
        .params(
            incident_id="PLACEHOLDER_ID",
            incident_title="PLACEHOLDER_TITLE",
            incident_severity="PLACEHOLDER_SEVERITY",
            incident_priority="PLACEHOLDER_PRIORITY",
            incident_body="PLACEHOLDER_DESCRIPTION",
            incident_url="PLACEHOLDER_URL",
            incident_source="PLACEHOLDER_SOURCE",
            incident_owner="PLACEHOLDER_OWNER",
            slack_channel_id="PLACEHOLDER_CHANNEL",
            notification_channels="#alerts",
            escalation_channel="#incident-escalation",
            investigation_timeout="3600",
            max_retries="3",
            investigation_agent="test-workflow",
            customer_impact="PLACEHOLDER_IMPACT",
            affected_services="PLACEHOLDER_SERVICES",
            dd_environment="na-integration",
            k8s_environment="p44-qa-integration",
            agent_uuid="1b0ed7bc-6385-40f8-8a62-bd9932bdadc2",
        )
        .env(
            KUBIYA_API_KEY="PLACEHOLDER_API_KEY",
            KUBIYA_USER_EMAIL="${KUBIYA_USER_EMAIL}",
            KUBIYA_USER_ORG="default",
            INCIDENT_SEVERITY="medium",
            INCIDENT_PRIORITY="medium"
        )
        .step("validate-incident", callback=lambda s:
            s.description("Validate incident parameters and prerequisites")
                .shell(
                    ValidateIncident(
                        incident_id="${incident_id}",
                        incident_title="${incident_title}",
                        incident_severity="${incident_severity}",
                        affected_services="${affected_services}",
                        incident_priority="${incident_priority}",
                        incident_owner="${incident_owner}",
                        incident_source="${incident_source}",
                        customer_impact="${customer_impact}",
                    ).get_command()
                )
                .output("validation_status"),
        )
        .step("setup-slack-integration", callback=lambda s:
            s.description("Initialize Slack integration for incident communications")
                .kubiya(
                    url="api/v1/integration/slack/token/1",
                    method="GET",
                    timeout=30,
                    silent=False,
                )
                .depends("validate-incident")
                .output("slack_token"),
        )
        .step("handle-validation-failure", callback=lambda s:
            s.description("Send Slack notification when services are missing and create validation agent")
                .shell(
                    ValidationFailure(
                        incident_id="${incident_id}",
                        incident_title="${incident_title}",
                        incident_severity="${incident_severity}",
                        channel="${slack_channel_id}",
                        affected_services="${affected_services}",
                        slack_token="${slack_token}",
                    ).get_command()
                )
                .depends("setup-slack-integration")
                .output("validation_failure_message"),
        )
        .step("get-observe-supported-datasets", callback=lambda s:
            s.description("Retrieve supported dataset IDs for Observe platform")
                .shell(
                    SupportedDatasets().get_command()
                )
                .depends("setup-slack-integration")
                .output("observe_supported_ds_ids"),
        )
        .step("get-datadog-metrics-config", callback=lambda s:
            s.description("Retrieve Datadog metrics configuration and key metrics for monitoring")
                .shell(
                    DatadogMetrics().get_command()
                )
                .depends("setup-slack-integration")
                .output("datadog_metrics_config"),
        )
        .step("prepare-copilot-context", callback=lambda s:
            s.description("Prepare context prompts for agent interactions")
                .shell(
                    CopilotContext(
                        incident_id="${incident_id}",
                        incident_title="${incident_title}",
                        incident_severity="${incident_severity}",
                        affected_services="${affected_services}",
                        incident_priority="${incident_priority}",
                        incident_source="${incident_source}",
                        incident_owner="${incident_owner}",
                        customer_impact="${customer_impact}",
                        datadog_metrics_config="${datadog_metrics_config}",
                        observe_supported_ds_ids="${observe_supported_ds_ids}",
                    ).get_command()
                )
                .depends("setup-slack-integration", "get-observe-supported-datasets", "get-datadog-metrics-config")
                .output("copilot_prompts"),
        )
        .step("post-incident-alert", callback=lambda s:
            s.description("Send beautiful incident alert to Slack when services are provided")
                .shell(
                    PostIncidentAlert(
                        incident_id="${incident_id}",
                        incident_title="${incident_title}",
                        incident_severity="${incident_severity}",
                        incident_priority="${incident_priority}",
                        affected_services="${affected_services}",
                        incident_body="${incident_body}",
                        incident_url="${incident_url}",
                        channel="${slack_channel_id}",
                        agent_uuid="${agent_uuid}",
                        copilot_prompt="${copilot_prompts}",
                        slack_token="${slack_token.token}",
                    ).get_command()
                )
                .depends("prepare-copilot-context")
                .output("initial_alert_message"),
        )
        .step("notify-investigation-start", callback=lambda s:
            s.description("Notify AI investigation start")
                .shell(
                    InvestigationStart(
                        investigation_agent="${investigation_agent}",
                        investigation_timeout="${investigation_timeout}",
                        affected_services="${affected_services}",
                        max_retries="${max_retries}",
                        slack_token="${slack_token.token}",
                        channel="${slack_channel_id}",
                    ).get_command()
                )
                .depends("post-incident-alert")
                .output("investigation_start_message"),
        )
        .step("investigate-kubernetes-cluster-health", callback=lambda s:
            s.description("AI-powered Kubernetes basic cluster health investigation")
                .agent(
                    name="test-workflow",
                    message=InvestigateKubernetesClusterHealth(
                                incident_id="${incident_id}",
                                incident_title="${incident_title}",
                                incident_severity="${incident_severity}",
                                datadog_metrics_config="${datadog_metrics_config}",
                            ).get_command(),
                )
                .timeout(3000)
                .retries(5)
                .depends("notify-investigation-start", "get-datadog-metrics-config")
                .output("kubernetes_cluster_health_results")
        )
        .step("investigate-service-specific", callback=lambda s:
            s.description("AI-powered service-specific investigation in service specific namespace")
                .agent(
                    name="test-workflow",
                    message=InvestigateServiceSpecific(
                        incident_id="${incident_id}",
                        incident_title="${incident_title}",
                        incident_severity="${incident_severity}",
                        affected_services="${affected_services}",
                        datadog_metrics_config="${datadog_metrics_config}",
                        observe_supported_ds_ids="${observe_supported_ds_ids}",
                        k8s_environment="${k8s_environment}",
                        dd_environment="${dd_environment}",
                    ).get_command()
                )
                .timeout(3000)
                .retries(5)
                .depends("investigate-kubernetes-cluster-health", "get-observe-supported-datasets", "get-datadog-metrics-config")
                .output("service_specific_results")
        )
        .step("create-incident-report", callback=lambda s:
            s.description("Create comprehensive incident report with TLDR summary using cleaned data")
                    .llm_completion(
                        model="gpt-4o",
                        temperature=0.3,
                        max_tokens=4096,
                        evaluate=True,
                        prompt=(m := IncidentReportData(
                            incident_id="${incident_id}",
                            incident_title="${incident_title}",
                            incident_severity="${incident_severity}",
                            affected_services="${affected_services}",
                            cleaned_cluster_results="${cleaned_cluster_results}",
                            cleaned_service_results="${cleaned_service_results}",
                        ).get_prompt()).prompt,
                        system_prompt=m.system_prompt
                    )
                    .timeout(300)
                    .retries(5)
                    .depends("clean-cluster-investigation", "clean-service-investigation")
                    .output("formatted_incident_report"),
        )
        .step("create-executive-summary", callback=lambda s:
                s.description("Create concise executive summary using LLM")
                    .llm_completion(
                        model="gpt-4o",
                        temperature=0.3,
                        max_tokens=2000,
                        evaluate=True,
                        json_mode=True,
                        prompt=(m := ExecutiveSummaryData(
                            incident_id="${incident_id}",
                            incident_title="${incident_title}",
                            incident_severity="${incident_severity}",
                            affected_services="${affected_services}",
                            formatted_incident_report="${formatted_incident_report}",
                        ).get_prompt()).prompt,
                        system_prompt=m.system_prompt
                    )
                .timeout(60)
                .retries(5)
                .depends("create-incident-report")
                .output("executive_summary"),
        )
        .step("clean-cluster-investigation", callback=lambda s:
                s.description("Clean cluster investigation output for LLM processing")
                    .llm_completion(
                        model="gpt-4o",
                        temperature=0.1,
                        max_tokens=4000,
                        evaluate=True,
                        prompt=(m := CleanClusterInvestigationData(
                            kubernetes_cluster_health_results="${kubernetes_cluster_health_results}",
                        ).get_prompt()).prompt,
                        system_prompt=m.system_prompt
                    )
                .timeout(30)
                .depends("investigate-kubernetes-cluster-health")
                .output("cleaned_cluster_results"),
        )
        .step("clean-service-investigation", callback=lambda s:
                s.description("Clean service investigation output for LLM processing")
                    .llm_completion(
                        model="gpt-4o",
                        temperature=0.1,
                        max_tokens=4000,
                        evaluate=True,
                        prompt=(m := CleanServiceInvestigationData(
                            service_specific_results="${service_specific_results}",
                        ).get_prompt()).prompt,
                        system_prompt=m.system_prompt
                    )
                .timeout(30)
                .depends("investigate-service-specific")
                .output("cleaned_service_results"),
        )
        .step("format-slack-reports", callback=lambda s:
                s.description("Format concise reports for Slack upload")
                    .llm_completion(
                        model="gpt-4o",
                        temperature=0.3,
                        max_tokens=3000,
                        evaluate=True,
                        prompt=(m := FormatSlackReportsData(
                            cleaned_cluster_results="${cleaned_cluster_results}",
                            cleaned_service_results="${cleaned_service_results}",
                        ).get_prompt()).prompt,
                        system_prompt=m.system_prompt
                    )
                .timeout(60)
                .retries(5)
                .depends("clean-cluster-investigation", "clean-service-investigation")
                .output("formatted_summaries"),
        )
        .step("upload-investigation-results", callback=lambda s:
                s.description("Upload investigation results as files to Slack and post summary")
                    .tool_def(
                        name="investigation-report-uploader",
                        description="Upload investigation results as files and post summary to Slack",
                        type="docker",
                        image="python:3.11-slim",
                        content=(m := InvestigationResults(
                            input_file="../input_files/investigation_results.py",
                            output_file="/tmp/upload_investigation_results.py",
                        )).get_command(),
                        with_files= m.get_files(),
                        config_args=[
                            {
                                "name": "slack_token_value",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "incident_id",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "incident_title",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "incident_severity",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "affected_services",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "slack_channel_id",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "incident_url",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "cluster_results",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "service_results",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "formatted_report",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "agent_uuid",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "deep_dive_prompt",
                                "type": "string",
                                "required": False
                            },
                            {
                                "name": "apply_fixes_prompt",
                                "type": "string",
                                "required": False
                            },
                            {
                                "name": "monitoring_prompt",
                                "type": "string",
                                "required": False
                            },
                            {
                                "name": "executive_summary",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "formatted_summaries",
                                "type": "string",
                                "required": True
                            }
                        ],
                        args={
                            "slack_token_value": "${slack_token.token}",
                            "incident_id": "${incident_id}",
                            "incident_title": "${incident_title}",
                            "incident_severity": "${incident_severity}",
                            "affected_services": "${affected_services}",
                            "slack_channel_id": "${slack_channel_id}",
                            "incident_url": "${incident_url}",
                            "cluster_results": "${kubernetes_cluster_health_results}",
                            "service_results": "${service_specific_results}",
                            "formatted_report": "${formatted_incident_report}",
                            "agent_uuid": "1b0ed7bc-6385-40f8-8a62-bd9932bdadc2",
                            "deep_dive_prompt": "${DEEP_DIVE_PROMPT}",
                            "apply_fixes_prompt": "${APPLY_FIXES_PROMPT}",
                            "monitoring_prompt": "${MONITORING_PROMPT}",
                            "executive_summary": "${executive_summary}",
                            "formatted_summaries": "${formatted_summaries}"
                        }
                )
                .depends("create-incident-report", "create-executive-summary", "format-slack-reports")
                .output("slack_post_status"),
        )
    )

    return wf
