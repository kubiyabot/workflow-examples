import abc
from abc import abstractmethod

from pydantic import BaseModel

from message_blocks.blocks import (
    Message,
    HeaderBlock,
    SectionBlock,
    MarkdownTextObject,
    PlainTextObject,
    DividerBlock,
    ActionsBlock,
    ButtonElement,
    ButtonStyle, ContextBlock, BlockType,
)


# ============================================================================
# BASE MESSAGE MODEL
# ============================================================================

class MessageModel(BaseModel, abc.ABC):

    @abstractmethod
    def to_message(self) -> Message:
        """Convert to SlackMessage."""
        raise NotImplementedError("Subclasses must implement this method.")


# ============================================================================
# INCIDENT RESPONSE MESSAGES
# ============================================================================

### START: ValidationFailureMessage ###
"""
Validation Failure Message
==========================
Purpose: Notify about validation failures when affected services are missing
Features:
- Display incident details with severity and ID
- Show agent creation with available tools count
- Provide guidance for next steps
- Clean incident information layout
Use Case: Incident response teams when service validation fails
"""
class ValidationFailureMessage(MessageModel):
    """Message for validation failure notifications when affected services are missing."""
    incident_title: str
    incident_id: str
    incident_severity: str
    channel: str
    agent_name: str = "incident-service-validator-TEMPLATE"
    tools_count: int = 5

    def to_message(self) -> Message:
        """Convert to SlackMessage."""
        return Message(
            channel=self.channel,
            text="🔍 Service Validation Agent Created",
            blocks=[
                HeaderBlock(
                    text=PlainTextObject(text="🔍 Service Validation Agent Created", emoji=True)
                ),
                SectionBlock(
                    fields=[
                        MarkdownTextObject(text=f"*Incident:*\n{self.incident_title}"),
                        MarkdownTextObject(text=f"*ID:*\n{self.incident_id}"),
                        MarkdownTextObject(text=f"*Severity:*\n{self.incident_severity}"),
                        MarkdownTextObject(text=f"*Agent:*\n{self.agent_name}"),
                    ]
                ),
                SectionBlock(
                    text=MarkdownTextObject(text=f"*Available Tools:* {self.tools_count} Kubernetes investigation tools")
                ),
                SectionBlock(
                    text=MarkdownTextObject(
                        text="The agent will help discover and validate affected services. Please provide the list of affected services when available."
                    )
                )
            ]
        )
### END: ValidationFailureMessage ###



### START: PostIncidentAlertMessage ###
"""
Post Incident Alert Message
===========================
Purpose: Alert about new incidents received for triage in production
Features:
- Display incident title, severity, and priority
- Show affected services and incident details
- Include action button to view on monitoring platform
- Automatic AI investigation notification
Use Case: Operations teams receiving production incident alerts
"""
class PostIncidentAlertMessage(MessageModel):
    incident_title: str
    incident_id: str
    incident_severity: str
    severity_emoji: str
    incident_priority: str
    affected_services: str
    incident_body: str
    incident_url: str
    channel: str

    def to_message(self) -> Message:

        return Message(
            channel=self.channel,
            text=f"🚨 INCIDENT: {self.incident_title}",
            blocks=[
                HeaderBlock(
                    text=PlainTextObject(text="🚨 Received incident to traige in PRODUCTION!", emoji=True)
                ),
                SectionBlock(
                    text=MarkdownTextObject(text=f"*{self.incident_title}*")
                ),
                SectionBlock(
                    fields=[
                        MarkdownTextObject(text=f"*ID:* {self.incident_id}"),
                        MarkdownTextObject(text=f"*Severity:* {self.severity_emoji} {self.incident_severity}"),
                        MarkdownTextObject(text=f"*Priority:* {self.incident_priority}"),
                        MarkdownTextObject(text=f"*Services:* {self.affected_services}")
                    ]
                ),
                DividerBlock(),
                SectionBlock(
                    text=MarkdownTextObject(text=f"{self.incident_body}")
                ),
                DividerBlock(),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text=PlainTextObject(text="📊 View on Datadog", emoji=True),
                            url=self.incident_url,
                            style=ButtonStyle.PRIMARY
                        )
                    ]
                ),
                ContextBlock(
                    type=BlockType.CONTEXT,
                    elements=[
                        MarkdownTextObject(text="⚡ AI investigation will begin automatically in a few seconds...")
                    ],
                ),
            ]
        )
### END: PostIncidentAlertMessage ###



### START: InvestigationProgressMessage ###
"""
Investigation Progress Message
==============================
Purpose: Show progress of AI-powered incident investigation
Features:
- Display investigation start notification
- Show multi-region agent status (NA/EU)
- Include ETA and partial results information
- Real-time investigation tracking
Use Case: Teams monitoring automated incident investigation progress
"""
class InvestigationProgressMessage(MessageModel):
    """Message for investigation progress notification."""
    channel: str
    incident_id: str
    incident_title: str
    incident_severity: str
    affected_services: str
    timeout_minutes: str

    def to_message(self) -> Message:
        return Message(
            channel=self.channel,
            text="🔍 AI Investigation Started",
            blocks=[
                SectionBlock(
                    text=MarkdownTextObject(text=f"🔍 *AI Investigation Started*\n{self.incident_title}")
                ),
                ContextBlock(
                    elements=[
                        MarkdownTextObject(
                            text=f"ID: {self.incident_id} | Severity: {self.incident_severity} | Services: {self.affected_services}")
                    ]
                ),
                DividerBlock(),
                SectionBlock(
                    fields=[
                        MarkdownTextObject(text="*🇺🇸 NA Agent*\n🟢 Analyzing..."),
                        MarkdownTextObject(text="*🇪🇺 EU Agent*\n🟢 Analyzing...")
                    ]
                ),
                ContextBlock(
                    elements=[
                        MarkdownTextObject(
                            text=f"⏱️ ETA: ~{self.timeout_minutes} minutes | 💡 Partial results will be provided even if steps fail")
                    ]
                )
            ]
        )
### END: InvestigationProgressMessage ###



### START: InvestigationResultsMessage ###
"""
Investigation Results Message
=============================
Purpose: Present completed AI investigation results and findings
Features:
- Display investigation completion status
- Show incident summary and key findings
- Include links to detailed investigation reports
- Timestamp for investigation completion
Use Case: Teams reviewing completed incident investigation results
"""
class InvestigationResultsMessage(MessageModel):
    """Message for investigation results notification."""
    channel: str
    incident_id: str
    incident_title: str
    incident_severity: str
    severity_emoji: str
    affected_services: str
    tldr_summary: str
    files_section: str
    timestamp: str

    def to_message(self) -> Message:
        return Message(
            channel=self.channel,
            text='✅ AI Investigation Complete',
            blocks=[
                HeaderBlock(
                    text=PlainTextObject(text="✅ AI INVESTIGATION COMPLETE", emoji=True)
                ),
                SectionBlock(
                    fields=[
                        MarkdownTextObject(text=f'*Incident:* {self.incident_id}'),
                        MarkdownTextObject(text=f'*Severity:* {self.severity_emoji} {self.incident_severity}'),
                        MarkdownTextObject(text=f'*Services:* {self.affected_services}'),
                        MarkdownTextObject(text=f'*Title:* {self.incident_title}'),
                    ]
                ),
                DividerBlock(),
                SectionBlock(
                    text=MarkdownTextObject(text=f'*🎯 Summary:*\n{self.tldr_summary}')
                ),
                DividerBlock(),
                SectionBlock(
                    text=MarkdownTextObject(text=f'*📄 Investigation Reports:*\n{self.files_section}')
                ),
                ContextBlock(
                    elements=[
                        MarkdownTextObject(text=f'_Investigation completed at {self.timestamp}_')
                    ]
                ),
            ]
        )
### END: InvestigationResultsMessage ###



# ============================================================================
# ADDITIONAL MESSAGE EXAMPLES
# ============================================================================

### START: DeploymentNotificationMessage ###
"""
Deployment Notification Message
===============================
Purpose: Notify about application deployment status and details
Features:
- Display deployment information with service details
- Show deployment status and version
- Include rollback button for failed deployments
- Environment and timestamp information
Use Case: DevOps teams tracking deployment progress
"""
class DeploymentNotificationMessage(MessageModel):
    """Message for deployment notifications with status and details."""
    channel: str
    service_name: str
    version: str
    environment: str
    deployment_status: str  # "success", "failed", "in_progress"
    deploy_time: str
    deployed_by: str
    commit_hash: str
    rollback_available: bool = True

    def to_message(self) -> Message:
        status_emoji = {
            "success": "✅",
            "failed": "❌", 
            "in_progress": "🔄"
        }.get(self.deployment_status, "🔄")
        
        blocks = [
            HeaderBlock(
                text=PlainTextObject(text=f"{status_emoji} Deployment {self.deployment_status.title()}", emoji=True)
            ),
            SectionBlock(
                fields=[
                    MarkdownTextObject(text=f"*Service:*\n{self.service_name}"),
                    MarkdownTextObject(text=f"*Version:*\n{self.version}"),
                    MarkdownTextObject(text=f"*Environment:*\n{self.environment}"),
                    MarkdownTextObject(text=f"*Deployed by:*\n{self.deployed_by}")
                ]
            ),
            SectionBlock(
                text=MarkdownTextObject(text=f"*Commit:* `{self.commit_hash}`\n*Time:* {self.deploy_time}")
            )
        ]
        
        if self.deployment_status == "failed" and self.rollback_available:
            blocks.append(
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text=PlainTextObject(text="🔄 Rollback", emoji=True),
                            style=ButtonStyle.DANGER
                        ),
                        ButtonElement(
                            text=PlainTextObject(text="📋 View Logs", emoji=True),
                            style=ButtonStyle.PRIMARY
                        )
                    ]
                )
            )
        
        return Message(
            channel=self.channel,
            text=f"{status_emoji} Deployment {self.deployment_status}: {self.service_name}",
            blocks=blocks
        )
### END: DeploymentNotificationMessage ###



### START: MaintenanceWindowMessage ###
"""
Maintenance Window Message
==========================
Purpose: Announce scheduled maintenance windows and affected services
Features:
- Display maintenance schedule with start/end times
- List affected services and expected impact
- Include preparation checklist and contact information
- Status updates during maintenance
Use Case: Operations teams communicating planned maintenance
"""
class MaintenanceWindowMessage(MessageModel):
    """Message for scheduled maintenance window notifications."""
    channel: str
    maintenance_title: str
    start_time: str
    end_time: str
    affected_services: list[str]
    impact_level: str  # "low", "medium", "high"
    maintenance_type: str  # "planned", "emergency"
    contact_person: str
    preparation_notes: str = ""

    def to_message(self) -> Message:
        impact_emoji = {
            "low": "🟡",
            "medium": "🟠", 
            "high": "🔴"
        }.get(self.impact_level, "🟡")
        
        type_emoji = "🚨" if self.maintenance_type == "emergency" else "🔧"
        
        services_text = "\n".join([f"• {service}" for service in self.affected_services])
        
        blocks = [
            HeaderBlock(
                text=PlainTextObject(text=f"{type_emoji} {self.maintenance_type.title()} Maintenance", emoji=True)
            ),
            SectionBlock(
                text=MarkdownTextObject(text=f"*{self.maintenance_title}*")
            ),
            SectionBlock(
                fields=[
                    MarkdownTextObject(text=f"*Start Time:*\n{self.start_time}"),
                    MarkdownTextObject(text=f"*End Time:*\n{self.end_time}"),
                    MarkdownTextObject(text=f"*Impact:*\n{impact_emoji} {self.impact_level.title()}"),
                    MarkdownTextObject(text=f"*Contact:*\n{self.contact_person}")
                ]
            ),
            DividerBlock(),
            SectionBlock(
                text=MarkdownTextObject(text=f"*Affected Services:*\n{services_text}")
            )
        ]
        
        if self.preparation_notes:
            blocks.extend([
                DividerBlock(),
                SectionBlock(
                    text=MarkdownTextObject(text=f"*Preparation Notes:*\n{self.preparation_notes}")
                )
            ])
        
        blocks.append(
            ContextBlock(
                elements=[
                    MarkdownTextObject(text="📞 For urgent issues during maintenance, contact the on-call engineer")
                ]
            )
        )
        
        return Message(
            channel=self.channel,
            text=f"{type_emoji} Maintenance: {self.maintenance_title}",
            blocks=blocks
        )
### END: MaintenanceWindowMessage ###



### START: SecurityAlertMessage ###
"""
Security Alert Message
======================
Purpose: Notify about security incidents and required actions
Features:
- Display security threat level and classification
- Show affected systems and recommended actions
- Include incident response timeline
- Emergency contact information
Use Case: Security teams responding to threats and vulnerabilities
"""
class SecurityAlertMessage(MessageModel):
    """Message for security alerts and incident notifications."""
    channel: str
    alert_title: str
    threat_level: str  # "low", "medium", "high", "critical"
    alert_type: str  # "vulnerability", "breach", "suspicious_activity"
    affected_systems: list[str]
    recommended_actions: list[str]
    incident_id: str
    reported_by: str
    report_time: str
    
    def to_message(self) -> Message:
        threat_emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠", 
            "critical": "🔴"
        }.get(self.threat_level, "🟡")
        
        type_emoji = {
            "vulnerability": "🛡️",
            "breach": "🚨",
            "suspicious_activity": "👁️"
        }.get(self.alert_type, "⚠️")
        
        systems_text = "\n".join([f"• {system}" for system in self.affected_systems])
        actions_text = "\n".join([f"• {action}" for action in self.recommended_actions])
        
        return Message(
            channel=self.channel,
            text=f"🚨 Security Alert: {self.alert_title}",
            blocks=[
                HeaderBlock(
                    text=PlainTextObject(text=f"{type_emoji} SECURITY ALERT", emoji=True)
                ),
                SectionBlock(
                    text=MarkdownTextObject(text=f"*{self.alert_title}*")
                ),
                SectionBlock(
                    fields=[
                        MarkdownTextObject(text=f"*Threat Level:*\n{threat_emoji} {self.threat_level.upper()}"),
                        MarkdownTextObject(text=f"*Type:*\n{self.alert_type.replace('_', ' ').title()}"),
                        MarkdownTextObject(text=f"*Incident ID:*\n{self.incident_id}"),
                        MarkdownTextObject(text=f"*Reported by:*\n{self.reported_by}")
                    ]
                ),
                DividerBlock(),
                SectionBlock(
                    text=MarkdownTextObject(text=f"*Affected Systems:*\n{systems_text}")
                ),
                DividerBlock(),
                SectionBlock(
                    text=MarkdownTextObject(text=f"*Recommended Actions:*\n{actions_text}")
                ),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text=PlainTextObject(text="🔒 View Details", emoji=True),
                            style=ButtonStyle.DANGER
                        ),
                        ButtonElement(
                            text=PlainTextObject(text="📋 Incident Response", emoji=True),
                            style=ButtonStyle.PRIMARY
                        )
                    ]
                ),
                ContextBlock(
                    elements=[
                        MarkdownTextObject(text=f"_Reported at {self.report_time} | Follow security protocols immediately_")
                    ]
                )
            ]
        )
### END: SecurityAlertMessage ###



### START: HealthCheckStatusMessage ###
"""
Health Check Status Message
===========================
Purpose: Display system health check results and service status
Features:
- Show overall system health with individual service status
- Display response times and availability metrics
- Include trending information and alerts
- Action buttons for quick remediation
Use Case: SRE teams monitoring system health and uptime
"""
class HealthCheckStatusMessage(MessageModel):
    """Message for system health check status notifications."""
    channel: str
    overall_status: str  # "healthy", "degraded", "unhealthy"
    check_timestamp: str
    services_status: dict[str, dict]  # service_name: {status, response_time, uptime}
    total_services: int
    healthy_services: int
    
    def to_message(self) -> Message:
        status_emoji = {
            "healthy": "🟢",
            "degraded": "🟡",
            "unhealthy": "🔴"
        }.get(self.overall_status, "🟡")
        
        service_fields = []
        for service_name, metrics in self.services_status.items():
            service_emoji = {
                "healthy": "🟢",
                "degraded": "🟡", 
                "unhealthy": "🔴"
            }.get(metrics.get("status", "unknown"), "⚪")
            
            response_time = metrics.get("response_time", "N/A")
            uptime = metrics.get("uptime", "N/A")
            
            service_fields.append(
                MarkdownTextObject(
                    text=f"*{service_name}:*\n{service_emoji} {metrics.get('status', 'unknown')} | {response_time}ms | {uptime}% uptime"
                )
            )
        
        blocks = [
            HeaderBlock(
                text=PlainTextObject(text=f"{status_emoji} System Health Check", emoji=True)
            ),
            SectionBlock(
                fields=[
                    MarkdownTextObject(text=f"*Overall Status:*\n{status_emoji} {self.overall_status.title()}"),
                    MarkdownTextObject(text=f"*Services:*\n{self.healthy_services}/{self.total_services} Healthy"),
                    MarkdownTextObject(text=f"*Last Check:*\n{self.check_timestamp}"),
                    MarkdownTextObject(text=f"*Availability:*\n{(self.healthy_services/self.total_services)*100:.1f}%")
                ]
            ),
            DividerBlock()
        ]
        
        # Add service status in chunks of 2 per section for better layout
        for i in range(0, len(service_fields), 2):
            fields_chunk = service_fields[i:i+2]
            blocks.append(SectionBlock(fields=fields_chunk))
        
        if self.overall_status != "healthy":
            blocks.extend([
                DividerBlock(),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text=PlainTextObject(text="🔧 Run Diagnostics", emoji=True),
                            style=ButtonStyle.PRIMARY
                        ),
                        ButtonElement(
                            text=PlainTextObject(text="📊 View Metrics", emoji=True),
                            style=ButtonStyle.DEFAULT
                        )
                    ]
                )
            ])
        
        blocks.append(
            ContextBlock(
                elements=[
                    MarkdownTextObject(text="🔄 Automated health checks run every 5 minutes")
                ]
            )
        )
        
        return Message(
            channel=self.channel,
            text=f"{status_emoji} Health Check: {self.overall_status}",
            blocks=blocks
        )
### END: HealthCheckStatusMessage ###



### START: BackupStatusMessage ###
"""
Backup Status Message
=====================
Purpose: Report backup operation status and storage information
Features:
- Display backup success/failure status with details
- Show backup size, duration, and storage location
- Include retention policy and next scheduled backup
- Quick access to restore operations
Use Case: Operations teams managing data backup and recovery
"""
class BackupStatusMessage(MessageModel):
    """Message for backup operation status notifications."""
    channel: str
    backup_name: str
    backup_status: str  # "success", "failed", "in_progress", "warning"
    backup_type: str  # "full", "incremental", "differential"
    start_time: str
    end_time: str = ""
    duration_minutes: int = 0
    backup_size: str = ""
    storage_location: str
    retention_days: int
    next_backup: str
    error_message: str = ""
    
    def to_message(self) -> Message:
        status_emoji = {
            "success": "✅",
            "failed": "❌",
            "in_progress": "🔄",
            "warning": "⚠️"
        }.get(self.backup_status, "🔄")
        
        type_emoji = {
            "full": "💾",
            "incremental": "📁",
            "differential": "📋"
        }.get(self.backup_type, "💾")
        
        blocks = [
            HeaderBlock(
                text=PlainTextObject(text=f"{status_emoji} Backup {self.backup_status.title()}", emoji=True)
            ),
            SectionBlock(
                text=MarkdownTextObject(text=f"{type_emoji} *{self.backup_name}* ({self.backup_type} backup)")
            ),
            SectionBlock(
                fields=[
                    MarkdownTextObject(text=f"*Status:*\n{status_emoji} {self.backup_status.title()}"),
                    MarkdownTextObject(text=f"*Start Time:*\n{self.start_time}"),
                    MarkdownTextObject(text=f"*Storage:*\n{self.storage_location}"),
                    MarkdownTextObject(text=f"*Retention:*\n{self.retention_days} days")
                ]
            )
        ]
        
        if self.backup_status != "in_progress":
            blocks.append(
                SectionBlock(
                    fields=[
                        MarkdownTextObject(text=f"*Duration:*\n{self.duration_minutes} minutes"),
                        MarkdownTextObject(text=f"*Size:*\n{self.backup_size}"),
                        MarkdownTextObject(text=f"*End Time:*\n{self.end_time}"),
                        MarkdownTextObject(text=f"*Next Backup:*\n{self.next_backup}")
                    ]
                )
            )
        
        if self.error_message:
            blocks.extend([
                DividerBlock(),
                SectionBlock(
                    text=MarkdownTextObject(text=f"*Error Details:*\n```{self.error_message}```")
                )
            ])
        
        if self.backup_status == "success":
            blocks.extend([
                DividerBlock(),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text=PlainTextObject(text="🔄 Restore", emoji=True),
                            style=ButtonStyle.PRIMARY
                        ),
                        ButtonElement(
                            text=PlainTextObject(text="📊 View History", emoji=True),
                            style=ButtonStyle.DEFAULT
                        )
                    ]
                )
            ])
        elif self.backup_status == "failed":
            blocks.extend([
                DividerBlock(),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text=PlainTextObject(text="🔄 Retry Backup", emoji=True),
                            style=ButtonStyle.DANGER
                        ),
                        ButtonElement(
                            text=PlainTextObject(text="📋 View Logs", emoji=True),
                            style=ButtonStyle.DEFAULT
                        )
                    ]
                )
            ])
        
        blocks.append(
            ContextBlock(
                elements=[
                    MarkdownTextObject(text="💡 Regular backups ensure data protection and business continuity")
                ]
            )
        )
        
        return Message(
            channel=self.channel,
            text=f"{status_emoji} Backup {self.backup_status}: {self.backup_name}",
            blocks=blocks
        )
### END: BackupStatusMessage ###



### START: EscalationNotificationMessage ###
"""
Escalation Notification Message
===============================
Purpose: Notify about incident escalation to higher priority level or different team
Features:
- Display escalation reason and timeline
- Show original and new priority/severity levels
- Include escalated team and contact information
- Provide escalation history and next steps
Use Case: Operations teams managing incident escalation workflows
"""
class EscalationNotificationMessage(MessageModel):
    """Message for incident escalation notifications."""
    channel: str
    incident_id: str
    incident_title: str
    original_severity: str
    new_severity: str
    original_priority: str
    new_priority: str
    escalation_reason: str
    escalated_to_team: str
    escalated_by: str
    escalation_time: str
    sla_breach_risk: bool = False
    estimated_resolution_time: str = ""
    on_call_contact: str = ""
    
    def to_message(self) -> Message:
        # Severity emojis
        severity_emojis = {
            "low": "🟢",
            "medium": "🟡", 
            "high": "🟠",
            "critical": "🔴"
        }
        
        original_emoji = severity_emojis.get(self.original_severity.lower(), "⚪")
        new_emoji = severity_emojis.get(self.new_severity.lower(), "⚪")
        
        # Priority indicators
        priority_arrows = {
            "p1": "🔺", "p2": "🔺", "p3": "🔺", "p4": "🔺",
            "low": "🔺", "medium": "🔺", "high": "🔺", "critical": "🔺"
        }
        
        blocks = [
            HeaderBlock(
                text=PlainTextObject(text="⬆️ INCIDENT ESCALATED", emoji=True)
            ),
            SectionBlock(
                text=MarkdownTextObject(text=f"*{self.incident_title}*")
            ),
            SectionBlock(
                fields=[
                    MarkdownTextObject(text=f"*Incident ID:*\n{self.incident_id}"),
                    MarkdownTextObject(text=f"*Escalated by:*\n{self.escalated_by}"),
                    MarkdownTextObject(text=f"*Escalated to:*\n{self.escalated_to_team}"),
                    MarkdownTextObject(text=f"*Time:*\n{self.escalation_time}")
                ]
            ),
            DividerBlock(),
            SectionBlock(
                text=MarkdownTextObject(text=f"*Escalation Changes:*")
            ),
            SectionBlock(
                fields=[
                    MarkdownTextObject(text=f"*Severity:*\n{original_emoji} {self.original_severity} → {new_emoji} {self.new_severity}"),
                    MarkdownTextObject(text=f"*Priority:*\n{self.original_priority} → {self.new_priority}")
                ]
            ),
            DividerBlock(),
            SectionBlock(
                text=MarkdownTextObject(text=f"*Escalation Reason:*\n{self.escalation_reason}")
            )
        ]
        
        # Add SLA warning if there's a breach risk
        if self.sla_breach_risk:
            blocks.extend([
                DividerBlock(),
                SectionBlock(
                    text=MarkdownTextObject(text="⚠️ *SLA Breach Risk Detected*\nImmediate attention required to meet service level agreements")
                )
            ])
        
        # Add additional information if available
        additional_fields = []
        if self.estimated_resolution_time:
            additional_fields.append(
                MarkdownTextObject(text=f"*Est. Resolution:*\n{self.estimated_resolution_time}")
            )
        if self.on_call_contact:
            additional_fields.append(
                MarkdownTextObject(text=f"*On-call Contact:*\n{self.on_call_contact}")
            )
        
        if additional_fields:
            blocks.extend([
                DividerBlock(),
                SectionBlock(fields=additional_fields)
            ])
        
        # Action buttons
        blocks.extend([
            DividerBlock(),
            ActionsBlock(
                elements=[
                    ButtonElement(
                        text=PlainTextObject(text="📞 Contact Team", emoji=True),
                        style=ButtonStyle.DANGER
                    ),
                    ButtonElement(
                        text=PlainTextObject(text="📋 View Details", emoji=True),
                        style=ButtonStyle.PRIMARY
                    ),
                    ButtonElement(
                        text=PlainTextObject(text="📊 Escalation History", emoji=True),
                        style=ButtonStyle.DEFAULT
                    )
                ]
            ),
            ContextBlock(
                elements=[
                    MarkdownTextObject(text="🔔 This incident requires immediate attention from the escalated team")
                ]
            )
        ])
        
        return Message(
            channel=self.channel,
            text=f"⬆️ Escalated: {self.incident_title}",
            blocks=blocks
        )
### END: EscalationNotificationMessage ###