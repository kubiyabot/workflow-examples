from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel
import requests

### START: TextType ###
"""
TextType Enum
=============
Purpose: Define text object types for Slack Block Kit
Supported Types:
- PLAIN_TEXT: Standard text without formatting
- MRKDWN: Markdown-formatted text with rich formatting
Usage: Used to specify text formatting in various Slack components
"""
class TextType(str, Enum):
    """Text object types for Slack Block Kit."""
    PLAIN_TEXT = "plain_text"
    MRKDWN = "mrkdwn"
### END: TextType ###

### START: BlockType ###
"""
BlockType Enum
==============
Purpose: Define block types for Slack Block Kit layout
Supported Types:
- HEADER: Large heading blocks for titles
- SECTION: Main content blocks with text and accessories
- DIVIDER: Visual separator blocks
- ACTIONS: Interactive element container blocks
- CONTEXT: Supplementary information blocks
Usage: Specifies the type of layout block being created
"""
class BlockType(str, Enum):
    """Block types for Slack Block Kit."""
    HEADER = "header"
    SECTION = "section"
    DIVIDER = "divider"
    ACTIONS = "actions"
    CONTEXT = "context"
### END: BlockType ###

### START: ElementType ###
"""
ElementType Enum
================
Purpose: Define interactive element types for Slack Block Kit
Supported Types:
- BUTTON: Clickable button elements
- STATIC_SELECT: Dropdown with predefined options
- EXTERNAL_SELECT: Dropdown with external data source
- USERS_SELECT: User picker dropdown
- CHANNELS_SELECT: Channel picker dropdown
- CONVERSATIONS_SELECT: Conversation picker dropdown
- IMAGE: Image display elements
- PLAIN_TEXT_INPUT: Text input fields
- CHECKBOXES: Checkbox group elements
- RADIO_BUTTONS: Radio button group elements
- DATEPICKER: Date selection elements
- TIMEPICKER: Time selection elements
- OVERFLOW: Overflow menu elements
Usage: Specifies the type of interactive element in blocks
"""
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
### END: ElementType ###

### START: ButtonStyle ###
"""
ButtonStyle Enum
================
Purpose: Define button styling options for Slack Block Kit
Supported Styles:
- PRIMARY: Green button for primary actions
- DANGER: Red button for destructive actions
Usage: Applied to button elements to indicate action importance
"""
class ButtonStyle(str, Enum):
    """Button styles for Slack Block Kit."""
    PRIMARY = "primary"
    DANGER = "danger"
### END: ButtonStyle ###

### START: AttachmentColor ###
"""
AttachmentColor Enum
====================
Purpose: Define common color schemes for message attachments
Supported Colors:
- GOOD: Green color for positive/success messages
- WARNING: Yellow color for warning messages
- DANGER: Red color for error/danger messages
Usage: Sets the color bar on the left side of attachments
"""
class AttachmentColor(str, Enum):
    """Common attachment colors."""
    GOOD = "good"
    WARNING = "warning"
    DANGER = "danger"
### END: AttachmentColor ###


### START: PlainTextObject ###
"""
PlainTextObject Class
=====================
Purpose: Model for plain text objects in Slack Block Kit
Features:
- Simple text without markdown formatting
- Optional emoji rendering control
- Used in buttons, headers, and other components
Attributes:
- type: Always "plain_text"
- text: The actual text content
- emoji: Whether to render emoji (optional)
"""
class PlainTextObject(BaseModel):
    """Plain text object for Slack Block Kit."""
    type: TextType = TextType.PLAIN_TEXT
    text: str
    emoji: Optional[bool] = None
### END: PlainTextObject ###

### START: MarkdownTextObject ###
"""
MarkdownTextObject Class
========================
Purpose: Model for markdown-formatted text objects in Slack Block Kit
Features:
- Rich text formatting with markdown syntax
- Support for bold, italic, links, code blocks
- Optional verbatim mode for literal formatting
Attributes:
- type: Always "mrkdwn"
- text: Markdown-formatted text content
- verbatim: Whether to disable auto-formatting (optional)
"""
class MarkdownTextObject(BaseModel):
    """Markdown text object for Slack Block Kit."""
    type: TextType = TextType.MRKDWN
    text: str
    verbatim: Optional[bool] = None
### END: MarkdownTextObject ###

### START: TextObject ###
"""
TextObject Union Type
=====================
Purpose: Union type for flexible text object handling
Types: PlainTextObject | MarkdownTextObject
Usage: Allows either plain text or markdown text objects
"""
TextObject = Union[PlainTextObject, MarkdownTextObject]
### END: TextObject ###


### START: ButtonElement ###
"""
ButtonElement Class
===================
Purpose: Model for interactive button elements in Slack Block Kit
Features:
- Clickable buttons with actions
- URL links or custom action handlers
- Styling options (primary, danger)
- Confirmation dialogs support
- Accessibility labeling
Attributes:
- type: Always "button"
- text: Button label (PlainTextObject)
- action_id: Unique identifier for button actions
- url: Optional URL for link buttons
- value: Optional value sent with button clicks
- style: Visual styling (primary/danger)
- confirm: Confirmation dialog configuration
- accessibility_label: Screen reader label
"""
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
### END: ButtonElement ###

### START: ImageElement ###
"""
ImageElement Class
==================
Purpose: Model for image elements in Slack Block Kit
Features:
- Display images within blocks
- Accessibility support with alt text
- Supports various image formats
Attributes:
- type: Always "image"
- image_url: URL of the image to display
- alt_text: Alternative text for accessibility
"""
class ImageElement(BaseModel):
    """Image element for Slack Block Kit."""
    type: ElementType = ElementType.IMAGE
    image_url: str
    alt_text: str
### END: ImageElement ###

### START: HeaderBlock ###
"""
HeaderBlock Class
=================
Purpose: Model for header blocks in Slack Block Kit
Features:
- Large, prominent text headings
- Section titles and page headers
- Limited to plain text only
Attributes:
- type: Always "header"
- text: Header text (PlainTextObject only)
- block_id: Optional unique identifier
"""
class HeaderBlock(BaseModel):
    """Header block for Slack Block Kit."""
    type: BlockType = BlockType.HEADER
    text: PlainTextObject
    block_id: Optional[str] = None
### END: HeaderBlock ###

### START: SectionBlock ###
"""
SectionBlock Class
==================
Purpose: Model for section blocks in Slack Block Kit
Features:
- Main content blocks with text
- Support for accessory elements (buttons, images)
- Multiple text fields support
- Most versatile block type
Attributes:
- type: Always "section"
- text: Main text content (plain or markdown)
- fields: Optional array of additional text fields
- accessory: Optional interactive element
- block_id: Optional unique identifier
"""
class SectionBlock(BaseModel):
    """Section block for Slack Block Kit."""
    type: BlockType = BlockType.SECTION
    text: Optional[TextObject] = None
    fields: Optional[List[TextObject]] = None
    accessory: Optional[Dict[str, Any]] = None
    block_id: Optional[str] = None
### END: SectionBlock ###

### START: DividerBlock ###
"""
DividerBlock Class
==================
Purpose: Model for divider blocks in Slack Block Kit
Features:
- Visual separation between content sections
- Simple horizontal line element
- No configurable content
Attributes:
- type: Always "divider"
- block_id: Optional unique identifier
"""
class DividerBlock(BaseModel):
    """Divider block for Slack Block Kit."""
    type: BlockType = BlockType.DIVIDER
    block_id: Optional[str] = None
### END: DividerBlock ###

### START: ActionsBlock ###
"""
ActionsBlock Class
==================
Purpose: Model for actions blocks in Slack Block Kit
Features:
- Container for interactive elements
- Support for multiple buttons and inputs
- Horizontal layout of elements
- Maximum 25 elements per block
Attributes:
- type: Always "actions"
- elements: Array of interactive elements (ButtonElement, etc.)
- block_id: Optional unique identifier
"""
class ActionsBlock(BaseModel):
    """Actions block for Slack Block Kit."""
    type: BlockType = BlockType.ACTIONS
    elements: List[ButtonElement]
    block_id: Optional[str] = None
### END: ActionsBlock ###

### START: ContextBlock ###
"""
ContextBlock Class
==================
Purpose: Model for context blocks in Slack Block Kit
Features:
- Supplementary information display
- Small text and image elements
- Muted visual appearance
- Good for metadata and secondary info
Attributes:
- type: Always "context"
- elements: Array of text and image elements
- block_id: Optional unique identifier
"""
class ContextBlock(BaseModel):
    """Context block for Slack Block Kit."""
    type: BlockType = BlockType.CONTEXT
    elements: List[Union[TextObject, ImageElement]]
    block_id: Optional[str] = None
### END: ContextBlock ###

### START: Block ###
"""
Block Union Type
================
Purpose: Union type for all Slack Block Kit block types
Types: HeaderBlock | SectionBlock | DividerBlock | ActionsBlock | ContextBlock
Usage: Allows any valid block type in block arrays
"""
Block = Union[HeaderBlock, SectionBlock, DividerBlock, ActionsBlock, ContextBlock]
### END: Block ###


### START: Attachment ###
"""
Attachment Class
================
Purpose: Model for message attachments in Slack
Features:
- Rich content formatting for messages
- Color-coded left border
- Support for blocks and legacy fields
- Author, title, and footer metadata
- Image and thumbnail support
- Fallback text for notifications
Attributes:
- color: Left border color (hex or named)
- blocks: Array of Block Kit blocks
- fallback: Plain text fallback
- author_name/link/icon: Author information
- title/title_link: Attachment title
- text: Main attachment text
- fields: Legacy field arrays
- image_url/thumb_url: Image attachments
- footer/footer_icon: Footer information
- ts: Timestamp for attachment
- actions: Legacy action buttons
- callback_id: Legacy callback identifier
- attachment_type: Legacy attachment type
"""
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
### END: Attachment ###

### START: Message ###
"""
Message Class
=============
Purpose: Complete Slack message model with full API integration
Features:
- Complete message structure for Slack API
- Block Kit and attachment support
- Thread support for conversations
- Message formatting and parsing options
- JSON serialization methods
- Direct Slack API posting capability
- Channel targeting and user identification
Attributes:
- channel: Target channel ID or name
- text: Main message text
- attachments: Optional array of Attachment objects
- blocks: Optional array of Block objects
- thread_ts: Optional thread timestamp for replies
- mrkdwn: Enable/disable markdown parsing
- username: Custom username for bot messages
- icon_emoji/icon_url: Custom avatar for bot messages
- parse: Link and mention parsing mode
- link_names: Enable @username and #channel linking
- unfurl_links/unfurl_media: Control link previews
Methods:
- to_dict(): Convert to dictionary for JSON
- to_json(): Convert to formatted JSON string
- send(token): Post message to Slack API
"""
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
### END: Message ###