from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel
import requests

class TextType(str, Enum):
    """Text object types for Slack Block Kit."""
    PLAIN_TEXT = "plain_text"
    MRKDWN = "mrkdwn"


class BlockType(str, Enum):
    """Block types for Slack Block Kit."""
    HEADER = "header"
    SECTION = "section"
    DIVIDER = "divider"
    ACTIONS = "actions"
    CONTEXT = "context"


class ElementType(str, Enum):
    """Element types for Slack Block Kit."""
    BUTTON = "button"
    STATIC_SELECT = "static_select"
    EXTERNAL_SELECT = "external_select"
    USERS_SELECT = "users_select"
    CHANNELS_SELECT = "channels_select"
    CONVERSATIONS_SELECT = "conversations_select"
    IMAGE = "image"
    PLAIN_TEXT_INPUT = "plain_text_input"
    CHECKBOXES = "checkboxes"
    RADIO_BUTTONS = "radio_buttons"
    DATEPICKER = "datepicker"
    TIMEPICKER = "timepicker"
    OVERFLOW = "overflow"


class ButtonStyle(str, Enum):
    """Button styles for Slack Block Kit."""
    PRIMARY = "primary"
    DANGER = "danger"


class AttachmentColor(str, Enum):
    """Common attachment colors."""
    GOOD = "good"
    WARNING = "warning"
    DANGER = "danger"


class PlainTextObject(BaseModel):
    """Plain text object for Slack Block Kit."""
    type: TextType = TextType.PLAIN_TEXT
    text: str
    emoji: Optional[bool] = None


class MarkdownTextObject(BaseModel):
    """Markdown text object for Slack Block Kit."""
    type: TextType = TextType.MRKDWN
    text: str
    verbatim: Optional[bool] = None


TextObject = Union[PlainTextObject, MarkdownTextObject]


class ButtonElement(BaseModel):
    """Button element for Slack Block Kit."""
    type: ElementType = ElementType.BUTTON
    text: PlainTextObject
    action_id: Optional[str] = None
    url: Optional[str] = None
    value: Optional[str] = None
    style: Optional[ButtonStyle] = None
    confirm: Optional[Dict[str, Any]] = None
    accessibility_label: Optional[str] = None


class ImageElement(BaseModel):
    """Image element for Slack Block Kit."""
    type: ElementType = ElementType.IMAGE
    image_url: str
    alt_text: str


class HeaderBlock(BaseModel):
    """Header block for Slack Block Kit."""
    type: BlockType = BlockType.HEADER
    text: PlainTextObject
    block_id: Optional[str] = None


class SectionBlock(BaseModel):
    """Section block for Slack Block Kit."""
    type: BlockType = BlockType.SECTION
    text: Optional[TextObject] = None
    fields: Optional[List[TextObject]] = None
    accessory: Optional[Dict[str, Any]] = None
    block_id: Optional[str] = None


class DividerBlock(BaseModel):
    """Divider block for Slack Block Kit."""
    type: BlockType = BlockType.DIVIDER
    block_id: Optional[str] = None


class ActionsBlock(BaseModel):
    """Actions block for Slack Block Kit."""
    type: BlockType = BlockType.ACTIONS
    elements: List[ButtonElement]
    block_id: Optional[str] = None


class ContextBlock(BaseModel):
    """Context block for Slack Block Kit."""
    type: BlockType = BlockType.CONTEXT
    elements: List[Union[TextObject, ImageElement]]
    block_id: Optional[str] = None


Block = Union[HeaderBlock, SectionBlock, DividerBlock, ActionsBlock, ContextBlock]


class Attachment(BaseModel):
    """Slack message attachment."""
    color: Optional[str] = None
    blocks: Optional[List[Block]] = None
    fallback: Optional[str] = None
    author_name: Optional[str] = None
    author_link: Optional[str] = None
    author_icon: Optional[str] = None
    title: Optional[str] = None
    title_link: Optional[str] = None
    text: Optional[str] = None
    fields: Optional[List[Dict[str, Any]]] = None
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    footer: Optional[str] = None
    footer_icon: Optional[str] = None
    ts: Optional[int] = None
    actions: Optional[List[Dict[str, Any]]] = None
    callback_id: Optional[str] = None
    attachment_type: Optional[str] = None


class Message(BaseModel):
    """Complete Slack message model."""
    channel: str
    text: str
    attachments: Optional[List[Attachment]] = None
    blocks: Optional[List[Block]] = None
    thread_ts: Optional[str] = None
    mrkdwn: Optional[bool] = None
    username: Optional[str] = None
    icon_emoji: Optional[str] = None
    icon_url: Optional[str] = None
    parse: Optional[str] = None
    link_names: Optional[bool] = None
    unfurl_links: Optional[bool] = None
    unfurl_media: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump(exclude_none=True)

    def to_json(self) -> str:
        """Convert to JSON"""
        return self.model_dump_json(exclude_none=True, indent=2)

    def send(self, token: str) -> int:

        """Send the message to the appropriate channel."""
        msg = self.model_dump(exclude_none=True)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        response = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=msg)
        return response.status_code