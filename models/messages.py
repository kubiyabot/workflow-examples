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

class MessageModel(BaseModel, abc.ABC):

    @abstractmethod
    def to_message(self) -> Message:
        """Convert to SlackMessage."""
        raise NotImplementedError("Subclasses must implement this method.")

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