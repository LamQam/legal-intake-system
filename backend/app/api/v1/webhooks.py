from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.whatsapp import WhatsAppWebhookPayload, WebhookPayload, WhatsAppWebhookVerification
from app.services.whatsapp.conversation_manager import ConversationManager
from app.models import Conversation, Message, User
from app.core.supabase import supabase
import logging
import hmac
import hashlib
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

async def verify_webhook_signature(request: Request, body: bytes) -> bool:
    """Verify WhatsApp webhook signature"""
    if not settings.meta_webhook_secret:
        logger.warning("Webhook secret not configured, skipping signature verification")
        return True

    try:
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not signature.startswith("sha256="):
            logger.warning("Invalid signature format")
            return False

        expected_signature = signature[7:]  # Remove "sha256=" prefix
        calculated_signature = hmac.new(
            settings.meta_webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, calculated_signature)
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False

async def handle_incoming_message(payload: WebhookPayload, db: Session):
    """Handle incoming WhatsApp message"""
    try:
        # Create or get user
        user = db.query(User).filter(User.phone == payload.phone).first()
        if not user:
            user = User(
                phone=payload.phone,
                full_name=f"WhatsApp User {payload.phone}",
                email=f"whatsapp_{payload.phone}@temp.local"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create or get conversation
        conversation = db.query(Conversation).filter(
            Conversation.phone_number == payload.phone,
            Conversation.status.in_(["new", "in_progress"])
        ).first()

        if not conversation:
            conversation = Conversation(
                client_id=user.id,
                phone_number=payload.phone,
                status="new",
                language="en"  # Will be updated by language detector
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Create message record
        message = Message(
            conversation_id=conversation.id,
            message_type=payload.message_type,
            content=payload.text,
            whatsapp_message_id=payload.whatsapp_message_id,
            is_from_user=True
        )
        db.add(message)
        db.commit()

        # Initialize conversation manager and handle the message
        manager = ConversationManager(payload.phone)
        await manager.handle_message(payload.text or "", {})

        # Update conversation status
        conversation.status = "in_progress"
        db.commit()

        logger.info(f"Processed message from {payload.phone}: {payload.text[:50]}...")

    except Exception as e:
        logger.error(f"Error handling incoming message: {e}")
        db.rollback()
        raise

@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    payload: WhatsAppWebhookPayload,
    db: Session = Depends(get_db)
):
    """
    Handle incoming WhatsApp webhooks.
    This endpoint receives messages from WhatsApp Business API.
    """
    try:
        # Verify webhook signature
        body = await request.body()
        if not await verify_webhook_signature(request, body):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Process the webhook payload
        message = payload.get_first_message()
        if not message:
            logger.info("No message found in webhook payload")
            return {"status": "ok", "message": "No message to process"}

        # Convert to internal payload format
        webhook_payload = WebhookPayload.from_whatsapp_webhook(payload)

        # Handle the message
        await handle_incoming_message(webhook_payload, db)

        return {"status": "ok", "message": "Message processed successfully"}

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/whatsapp")
async def whatsapp_webhook_verify(
    hub_mode: str,
    hub_challenge: str,
    hub_verify_token: str
):
    """
    Verify WhatsApp webhook during setup.
    Meta uses this endpoint to verify the webhook URL.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_verify_token:
        logger.info("WhatsApp webhook verified successfully")
        return {"hub.challenge": hub_challenge}
    else:
        logger.warning(f"WhatsApp webhook verification failed: mode={hub_mode}, token={hub_verify_token}")
        raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/whatsapp/status")
async def whatsapp_status_webhook(payload: dict):
    """
    Handle WhatsApp message status updates (delivered, read, failed, etc.)
    """
    try:
        # Log status updates for monitoring
        logger.info(f"WhatsApp status update: {payload}")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Status webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")