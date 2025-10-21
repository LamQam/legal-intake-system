from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class WhatsAppContact(BaseModel):
    """WhatsApp contact information"""
    profile: Optional[Dict[str, Any]] = None
    wa_id: str = Field(..., description="WhatsApp ID of the contact")

class WhatsAppMessage(BaseModel):
    """WhatsApp message content"""
    from_: Optional[str] = Field(None, alias="from")
    id: str = Field(..., description="Message ID")
    timestamp: Optional[str] = None
    type: str = Field(..., description="Message type (text, image, etc.)")
    context: Optional[Dict[str, Any]] = None

    # Text message fields
    text: Optional[Dict[str, str]] = None

    # Media message fields
    image: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None
    audio: Optional[Dict[str, Any]] = None
    document: Optional[Dict[str, Any]] = None
    sticker: Optional[Dict[str, Any]] = None

    # Interactive message fields
    interactive: Optional[Dict[str, Any]] = None

    # Location message fields
    location: Optional[Dict[str, Any]] = None

    # Contact message fields
    contacts: Optional[List[Dict[str, Any]]] = None

    class Config:
        allow_population_by_field_name = True

class WhatsAppWebhookEntry(BaseModel):
    """WhatsApp webhook entry"""
    id: str = Field(..., description="Entry ID")
    changes: List[Dict[str, Any]] = Field(..., description="List of changes")
    messaging_product: str = Field(default="whatsapp")
    time: Optional[int] = None

class WhatsAppValue(BaseModel):
    """WhatsApp webhook value"""
    messaging_product: str = Field(default="whatsapp")
    metadata: Optional[Dict[str, Any]] = None
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessage]] = None

class WhatsAppStatus(BaseModel):
    """WhatsApp message status"""
    id: str = Field(..., description="Message ID")
    status: str = Field(..., description="Message status")
    timestamp: str = Field(..., description="Status timestamp")
    recipient_id: str = Field(..., description="Recipient WhatsApp ID")
    conversation: Optional[Dict[str, Any]] = None
    pricing: Optional[Dict[str, Any]] = None

class WhatsAppWebhookPayload(BaseModel):
    """Complete WhatsApp webhook payload"""
    object: str = Field(..., description="Always 'whatsapp_business_account'")
    entry: List[WhatsAppWebhookEntry] = Field(..., description="Webhook entries")

    def get_first_message(self) -> Optional[WhatsAppMessage]:
        """Extract the first message from the webhook payload"""
        for entry in self.entry:
            for change in entry.changes:
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    if messages:
                        return WhatsAppMessage(**messages[0])
        return None

    def get_phone_number(self) -> Optional[str]:
        """Extract phone number from the webhook payload"""
        for entry in self.entry:
            for change in entry.changes:
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    if messages and messages[0].get("from"):
                        return messages[0]["from"]
        return None

    def get_message_text(self) -> Optional[str]:
        """Extract message text from the webhook payload"""
        message = self.get_first_message()
        if message and message.text:
            return message.text.get("body")
        return None

    def get_message_type(self) -> Optional[str]:
        """Extract message type from the webhook payload"""
        message = self.get_first_message()
        return message.type if message else None

class WebhookPayload(BaseModel):
    """Simplified payload for internal processing"""
    phone: str = Field(..., description="Phone number of the sender")
    text: Optional[str] = Field(None, description="Message text content")
    message_type: str = Field(default="text", description="Type of message")
    whatsapp_message_id: str = Field(..., description="WhatsApp message ID")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")
    media_url: Optional[str] = Field(None, description="Media URL if present")
    media_type: Optional[str] = Field(None, description="Media type if present")

    @classmethod
    def from_whatsapp_webhook(cls, webhook_payload: WhatsAppWebhookPayload) -> "WebhookPayload":
        """Create WebhookPayload from WhatsApp webhook"""
        phone = webhook_payload.get_phone_number()
        text = webhook_payload.get_message_text()
        message = webhook_payload.get_first_message()

        return cls(
            phone=phone,
            text=text,
            message_type=webhook_payload.get_message_type() or "text",
            whatsapp_message_id=message.id if message else "",
            timestamp=datetime.fromtimestamp(int(message.timestamp)) if message and message.timestamp else None,
            media_url=None,  # Would need to download media from WhatsApp API
            media_type=None
        )

class WhatsAppMediaUpload(BaseModel):
    """Response for media upload"""
    media_id: str = Field(..., description="WhatsApp media ID")

class WhatsAppMessageResponse(BaseModel):
    """Response for sending WhatsApp message"""
    messaging_product: str = "whatsapp"
    recipient_type: str = "individual"
    to: str = Field(..., description="Recipient phone number")
    type: str = Field(..., description="Message type")
    text: Optional[Dict[str, str]] = None
    image: Optional[Dict[str, Any]] = None
    document: Optional[Dict[str, Any]] = None

class WhatsAppWebhookVerification(BaseModel):
    """Payload for webhook verification"""
    hub_mode: str = Field(..., description="Mode of the request")
    hub_challenge: str = Field(..., description="Challenge token")
    hub_verify_token: str = Field(..., description="Verification token")