from enum import Enum
from app.core.redis import redis_client
from app.services.whatsapp.client import send_message
from app.services.ai.language_detector import detect_language

class ConversationState(Enum):
    GREETING = "greeting"
    CONSENT = "consent"
    LANGUAGE = "language"
    MATTER_TYPE = "matter_type"
    DESCRIPTION = "description"
    JURISDICTION = "jurisdiction"
    DOCUMENT_UPLOAD = "document_upload"
    CONTACT_INFO = "contact_info"
    SUMMARY = "summary"
    HANDOVER = "handover"

class ConversationManager:
    def __init__(self, phone_number: str):
        self.phone = phone_number
        self.state_key = f"conv:{phone_number}"
    
    async def get_state(self) -> ConversationState:
        state = await redis_client.get(self.state_key)
        return ConversationState(state) if state else ConversationState.GREETING
    
    async def set_state(self, state: ConversationState):
        await redis_client.set(self.state_key, state.value, ex=86400)  # 24h TTL
    
    async def handle_message(self, message: str, media: dict = None):
        state = await self.get_state()
        lang = await detect_language(message)
        
        if state == ConversationState.GREETING:
            return await self._handle_greeting(lang)
        elif state == ConversationState.CONSENT:
            return await self._handle_consent(message, lang)
        # ... etc