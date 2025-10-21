from fastapi import APIRouter, Request, HTTPException
from app.services.whatsapp.message_handler import handle_incoming_message
from app.schemas.whatsapp import WebhookPayload
import hmac
import hashlib

router = APIRouter()

@router.get("/whatsapp")
async def verify_webhook(request: Request):
    """Meta webhook verification"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == "YOUR_VERIFY_TOKEN":
        return int(challenge)
    raise HTTPException(status_code=403)

@router.post("/whatsapp")
async def whatsapp_webhook(payload: WebhookPayload):
    """Handle incoming WhatsApp messages"""
    # Verify signature (HMAC)
    # Extract message, sender
    # Route to message_handler
    await handle_incoming_message(payload)
    return {"status": "ok"}