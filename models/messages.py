import abc
from abc import abstractmethod

from pydantic import BaseModel

from message_blocks.blocks import (
    Message,
    HeaderBlock,
    SectionBlock,
    MarkdownTextObject,
    PlainTextObject,
    Attachment,
    DividerBlock,
    ActionsBlock,
    ButtonElement,
    ButtonStyle,
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
    incident_priority: str
    affected_services: str
    incident_body: str
    incident_url: str
    agent_uuid: str
    channel: str
    copilot_prompt: str = ""

    def to_message(self) -> Message:
        """Convert to SlackMessage."""
        return Message(
            channel=self.channel,
            text=f"🚨 INCIDENT: {self.incident_title}",
            attachments=[
                Attachment(
                    color="danger",
                    blocks=[
                        HeaderBlock(
                            text=PlainTextObject(text="🚨 PRODUCTION INCIDENT ALERT")
                        ),
                        SectionBlock(
                            text=MarkdownTextObject(text=f"*{self.incident_title}*")
                        ),
                        DividerBlock(),
                        SectionBlock(
                            fields=[
                                MarkdownTextObject(text=f"*🆔 ID:*\n{self.incident_id}"),
                                MarkdownTextObject(text=f"*🔥 Severity:*\n{self.incident_severity}"),
                                MarkdownTextObject(text=f"*⚡ Priority:*\n{self.incident_priority}"),
                                MarkdownTextObject(text=f"*🎯 Services:*\n{self.affected_services}")
                            ]
                        ),
                        SectionBlock(
                            text=MarkdownTextObject(text=f"*📝 Description:*\n{self.incident_body}")
                        ),
                        ActionsBlock(
                            elements=[
                                ButtonElement(
                                    text=PlainTextObject(text="📊 Dashboard", emoji=True),
                                    url=self.incident_url,
                                    style=ButtonStyle.PRIMARY
                                ),
                                ButtonElement(
                                    text=PlainTextObject(text="🤖 Co-Pilot Mode", emoji=True),
                                    style=ButtonStyle.PRIMARY,
                                    value=str({"agent_uuid": self.agent_uuid, "message": self.copilot_prompt}),
                                    action_id="agent.process_message_1"
                                )
                            ]
                        )
                    ]
                )
            ]
        )


class InvestigationStartMessage(MessageModel):
    """Message for investigation start notification."""
    channel: str
    investigation_agent: str
    investigation_timeout: str
    max_retries: str

    def to_message(self) -> Message:
        return Message(
            channel=self.channel,
            text="🔍 AI Investigation Starting",
            attachments=[
                Attachment(
                    color="#ff9900",
                    blocks=[
                        HeaderBlock(
                            text=PlainTextObject(text="🔍 AI INVESTIGATION STARTING")
                        ),
                        SectionBlock(
                            fields=[
                                MarkdownTextObject(text=f"*Agent:*\n{self.investigation_agent or "test-workflow"}"),
                                MarkdownTextObject(text=f"*Timeout:*\n{self.investigation_timeout}s"),
                                MarkdownTextObject(text=f"*Retries:*\n{self.max_retries or "3"}"),
                            ]
                        ),
                        SectionBlock(
                            text=MarkdownTextObject(text="AI agent is now investigating the incident. Results will be posted here when complete.")
                        )
                    ]
                )
            ]
        )