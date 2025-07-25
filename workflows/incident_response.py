def generate_incident_response_workflow() -> 'Workflow':

    from kubiya_workflow_sdk.dsl import Workflow
    from models.models import (
        ValidateIncident,
        NormalizeChannelNameCommand,
        ValidationFailure,
        SupportedDatasets,
        DatadogMetrics,
        CopilotContext,
        PostIncidentAlert,
        InvestigationProgress,
        InvestigateNAClusterHealth,
        InvestigateEUClusterHealth,
        IncidentReport,
        ExecutiveSummary,
        CleanNAInvestigation,
        CleanEUInvestigation,
        FormatSlackReports,
        InvestigationResults,
    )
    wf = (
        Workflow("production-incident-workflow")
        .description("Production-grade incident response workflow with AI investigation and Slack integration")
        .params(
            incident_id="549",
            incident_title="testing kubiya parcel service is down",
            incident_severity="UNKNOWN",
            incident_priority="PLACEHOLDER_PRIORITY",
            incident_body="Status: Active | Severity: Unknown | Commander: Abhishek Sharma\nhttps://p44.datadoghq.com/incidents/549",
            incident_url="https://p44.datadoghq.com/incidents/549",
            incident_source="PLACEHOLDER_SOURCE",
            incident_owner="PLACEHOLDER_OWNER",
            slack_channel_id="#inc-549-testing kubiya parcel service is down",
            notification_channels="#alerts",
            escalation_channel="#incident-escalation",
            investigation_timeout="3600",
            max_retries="3",
            investigation_agent="test-workflow",
            customer_impact="PLACEHOLDER_IMPACT",
            affected_services= "parcel-service",
            dd_environment="na-integration",
            k8s_environment="p44-qa-integration",
            agent_uuid="1b0ed7bc-6385-40f8-8a62-bd9932bdadc2",
            normalize_channel_name="false"
        )
        .env(
            KUBIYA_API_KEY="${KUBIYA_API_KEY}",
            KUBIYA_USER_EMAIL="${KUBIYA_USER_EMAIL}",
            INCIDENT_SEVERITY="medium",
            INCIDENT_PRIORITY="medium"
        )
        # .timeout(1800)
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
        .step("normalize-channel-name", callback=lambda s:
            s.description("Normalize the channel name by replacing spaces with underscores")
                .shell(
                    NormalizeChannelNameCommand(
                        slack_channel_id="${slack_channel_id}",
                        normalize_channel_name="${normalize_channel_name:-true}",
                    ).get_command(),
                    with_config=False
                )
                .depends("validate-incident")
                .output("NORMALIZED_CHANNEL_NAME"),
        )
        .step("setup-slack-integration", callback=lambda s:
            s.description("Initialize Slack integration for incident communications")
                .kubiya(
                    url="api/v1/integration/slack/token/1",
                    method="GET",
                    silent=False,
                )
                .depends("normalize-channel-name")
                .output("slack_token"),
        )
        .step("validation_failure_message", callback=lambda s:
            s.description("Prepare validation failure message if parameters are missing")
                .shell(
                    ValidationFailure(
                        missing_params="${MISSING_PARAMS}"
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
                        incident_priority="${incident_priority:-Not Set}",
                        affected_services="${affected_services}",
                        incident_body="${incident_body}",
                        incident_url="${incident_url}",
                        channel="${NORMALIZED_CHANNEL_NAME}",
                        slack_token="${slack_token.token}",
                    ).get_command()
                )
                .depends("prepare-copilot-context")
                .output("initial_alert_message"),
        )
        .step("notify-investigation-progress", callback=lambda s:
            s.description("Post consolidated investigation progress update")
                .shell(
                    InvestigationProgress(
                        incident_id="${incident_id}",
                        investigation_timeout="${investigation_timeout:-300}",
                        channel="${NORMALIZED_CHANNEL_NAME}",
                        incident_title="${incident_title}",
                        incident_severity="${incident_severity}",
                        affected_services="${affected_services}",
                        slack_token="${slack_token.token}",
                    ).get_command()
                )
                .depends("post-incident-alert")
                .output("investigation_progress_message"),
        )
        .step("investigate-na-cluster-health", callback=lambda s:
            s.description("AI-powered cross-cluster investigation for NA Production")
                .agent(
                    name="p44-na-prod-incident-workflow",
                    message=InvestigateNAClusterHealth(
                                incident_id="{{.incident_id}}",
                                incident_title="{{.incident_title}}"
                            ).get_command(),
                )
                .timeout(300)
                .retry(
                    limit=3,
                    interval_sec=10,
                    # backoff=2.0,
                    # max_interval_sec=60,
                )
                .continue_on(
                    failure=True,
                    mark_success=False,
                    output=[
                        "ERROR: Sorry, I had an issue",
                        "Agent-manager not found",
                        "Stream error",
                        "INTERNAL_ERROR",
                        "stream ID",
                        "received from peer",
                        "re:stream error.*INTERNAL_ERROR",
                        "exit code 1",
                        "API key",
                        "command failed",
                        "Kubiya CLI"
                    ],
                )
                .depends("notify-investigation-progress", "get-datadog-metrics-config", "get-observe-supported-datasets")
                .output("na_cluster_results")
        )
        .step("investigate-eu-cluster-health", callback=lambda s:
            s.description("AI-powered cross-cluster investigation for EU Production")
                .agent(
                    name="p44-eu-prod-incident-workflow",
                    message=InvestigateEUClusterHealth(
                        incident_id="{{.incident_id}}",
                        incident_title="{{.incident_title}}"
                    ).get_command(),
                )
            .timeout(300)
            .retry(
                limit=3,
                interval_sec=10,
                # backoff=2.0,
                # max_interval_sec=60,
            )
            .continue_on(
                failure=True,
                mark_success=False,
                output=[
                    "ERROR: Sorry, I had an issue",
                    "Agent-manager not found",
                    "Stream error",
                    "INTERNAL_ERROR",
                    "stream ID",
                    "received from peer",
                    "re:stream error.*INTERNAL_ERROR",
                    "exit code 1",
                    "API key",
                    "command failed",
                    "Kubiya CLI"
                ],
            )
            .depends("notify-investigation-progress", "get-datadog-metrics-config", "get-observe-supported-datasets")
            .output("eu_cluster_results")
        )
        .step("create-incident-report", callback=lambda s:
            s.description("Create comprehensive incident report with TLDR summary using cleaned data")
                .agent(
                    name="p44-na-prod-incident-workflow",
                    message=IncidentReport(
                        incident_id="{{.incident_id}}",
                        incident_title="{{.incident_title}}",
                        incident_severity="{{.incident_severity}}",
                        affected_services="{{.affected_services}}",
                        cleaned_na_results="{{.cleaned_na_results}}",
                        cleaned_eu_results="{{.cleaned_eu_results}}",
                    ).get_command(),
                )
            .timeout(900)
            .retry(
                limit=5,
                interval_sec=10,
                # backoff=2.0,
                # max_interval_sec=120,
            )
            .continue_on(
                failure=True,
                mark_success=False,
                output=[
                    "Stream error",
                    "INTERNAL_ERROR",
                    "Agent-manager not found",
                    "exit code 1",
                    "API key",
                    "command failed",
                    "Kubiya CLI",
                    "re:exit code [0-9]+",
                    "re:failed.*agent"
                ],
            )
            .depends("clean-na-investigation", "clean-eu-investigation")
            .output("formatted_incident_report")
        )
        .step("create-executive-summary", callback=lambda s:
            s.description("Create concise executive summary using agent")
                .agent(
                    name="p44-na-prod-incident-workflow",
                    message=ExecutiveSummary(
                        incident_id="{{.incident_id}}",
                        incident_title="{{.incident_title}}",
                        incident_severity="{{.incident_severity}}",
                        affected_services="{{.affected_services}}",
                        formatted_incident_report="{{.formatted_incident_report}}",
                    ).get_command(),
                )
                .timeout(900)
                .retry(
                    limit=5,
                    interval_sec=10,
                    # backoff=2.0,
                    # max_interval_sec=120,
                )
                .continue_on(
                    failure=True,
                    mark_success=False,
                    output=[
                        "Stream error",
                        "INTERNAL_ERROR",
                        "Agent-manager not found",
                        "exit code 1",
                        "API key",
                        "command failed",
                        "Kubiya CLI",
                        "re:exit code [0-9]+",
                        "re:failed.*agent"
                    ],
                )
                .depends("create-incident-report")
                .output("executive_summary")
        )
        .step("clean-na-investigation", callback=lambda s:  # +
            s.description("Clean NA cluster investigation output for LLM processing")
                .agent(
                    name="p44-na-prod-incident-workflow",
                    message=CleanNAInvestigation(
                        na_cluster_results="{{.na_cluster_results}}",
                    ).get_command(),
                )
                .timeout(900)
                .retry(
                    limit=5,
                    interval_sec=10,
                    # backoff=2.0,
                    # max_interval_sec=120,
                )
                .continue_on(
                    failure=True,
                    mark_success=False,
                    output=[
                        "Agent-manager not found",
                        "ERROR:",
                        "Stream error",
                        "INTERNAL_ERROR",
                        "stream ID",
                        "re:stream error.*INTERNAL_ERROR",
                        "exit code 1",
                        "API key",
                        "command failed",
                        "Kubiya CLI",
                        "re:exit code [0-9]+",
                        "re:failed.*agent"
                    ],
                )
                .depends("investigate-na-cluster-health")
                .output("cleaned_na_results")
        )
        .step("clean-eu-investigation", callback=lambda s:  # +
            s.description("Clean EU cluster investigation output for LLM processing")
                .agent(
                    name="p44-eu-prod-incident-workflow",
                    message=CleanEUInvestigation(
                        eu_cluster_results="{{.eu_cluster_results}}",
                    ).get_command(),
                )
                .timeout(900)
                .retry(
                    limit=5,
                    interval_sec=10,
                    # backoff=2.0,
                    # max_interval_sec=120,
                )
                .continue_on(
                    failure=True,
                    mark_success=False,
                    output=[
                        "Agent-manager not found",
                        "ERROR:",
                        "Stream error",
                        "INTERNAL_ERROR",
                        "stream ID",
                        "re:stream error.*INTERNAL_ERROR",
                        "exit code 1",
                        "API key",
                        "command failed",
                        "Kubiya CLI",
                        "re:exit code [0-9]+",
                        "re:failed.*agent"
                    ],
                )
                .depends("investigate-eu-cluster-health")
                .output("cleaned_eu_results")
        )
        .step("format-slack-reports", callback=lambda s:  # +
            s.description("Format concise reports for Slack upload")
                .agent(
                    name="p44-eu-prod-incident-workflow",
                    message=FormatSlackReports(
                        cleaned_na_results="{{.cleaned_na_results}}",
                        cleaned_eu_results="{{.cleaned_eu_results}}",
                    ).get_command(),
                )
                .timeout(900)
                .retry(
                    limit=5,
                    interval_sec=10,
                    # backoff=2.0,
                    # max_interval_sec=120,
                )
                .continue_on(
                    failure=True,
                    mark_success=False,
                    output=[
                        "Stream error",
                        "INTERNAL_ERROR",
                        "Agent-manager not found",
                        "exit code 1",
                        "API key",
                        "command failed",
                        "Kubiya CLI",
                        "re:exit code [0-9]+",
                        "re:failed.*agent"
                    ],
                )
                .depends("clean-na-investigation", "clean-eu-investigation")
                .output("formatted_summaries")
        )
        .step("upload-investigation-results", callback=lambda s:
                s.description("Upload investigation results as files to Slack and post summary")
                    .tool_def(
                        name="investigation-report-uploader",
                        description="Upload investigation results as files and post summary to Slack",
                        type="docker",
                        image="python:3.11-slim",
                        content=(m := InvestigationResults(
                            input_file="./input_files/investigation_results.py",
                            output_file="/tmp/upload_results.py",
                        )).get_command(),
                        with_files= m.get_files(),
                        config_args=[
                            {
                                "name": "slack_token",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "channel",
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
                                "name": "executive_summary",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "formatted_report",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "na_results",
                                "type": "string",
                                "required": True
                            },
                            {
                                "name": "eu_results",
                                "type": "string",
                                "required": True
                            },
                        ],
                        args={
                            "slack_token": "${slack_token.token}",
                            "channel": "${NORMALIZED_CHANNEL_NAME}",
                            "incident_id": "${incident_id}",
                            "incident_title": "${incident_title}",
                            "incident_severity": "${incident_severity}",
                            "affected_services": "${affected_services}",
                            "executive_summary": "${executive_summary}",
                            "formatted_report": "${formatted_incident_report}",
                            "na_results": "${cleaned_na_results}",
                            "eu_results": "${cleaned_eu_results}"
                        }
                    )
                    .continue_on(
                        failure=True,
                    )
                    .depends( "create-incident-report", "create-executive-summary", "format-slack-reports")
                    .output("upload_summary_status")
        )
    )

    return wf
