from enum import Enum
from app.services.whatsapp.client import send_message
from app.services.ai.language_detector import detect_language
import logging

logger = logging.getLogger(__name__)

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
    """
    Manages WhatsApp conversation flow for legal intake.
    Uses in-memory storage for now (can be upgraded to Redis later).
    """

    def __init__(self, phone_number: str):
        self.phone = phone_number
        self.state_key = f"conv:{phone_number}"
        # In-memory storage for conversation states (replace with Redis later)
        self._memory_store = {}

    async def get_state(self) -> ConversationState:
        """Get current conversation state"""
        state = self._memory_store.get(self.state_key)
        return ConversationState(state) if state else ConversationState.GREETING

    async def set_state(self, state: ConversationState):
        """Set conversation state"""
        self._memory_store[self.state_key] = state.value
        logger.info(f"Set conversation state for {self.phone}: {state.value}")

    async def handle_message(self, message: str, media: dict = None):
        """Handle incoming WhatsApp message"""
        state = await self.get_state()
        lang = await detect_language(message)

        logger.info(f"Handling message in state {state.value} for {self.phone}")

        if state == ConversationState.GREETING:
            return await self._handle_greeting(lang)
        elif state == ConversationState.CONSENT:
            return await self._handle_consent(message, lang)
        elif state == ConversationState.LANGUAGE:
            return await self._handle_language_selection(message, lang)
        elif state == ConversationState.MATTER_TYPE:
            return await self._handle_matter_type(message, lang)
        elif state == ConversationState.DESCRIPTION:
            return await self._handle_description(message, lang)
        elif state == ConversationState.JURISDICTION:
            return await self._handle_jurisdiction(message, lang)
        elif state == ConversationState.DOCUMENT_UPLOAD:
            return await self._handle_document_upload(message, lang, media)
        elif state == ConversationState.CONTACT_INFO:
            return await self._handle_contact_info(message, lang)
        elif state == ConversationState.SUMMARY:
            return await self._handle_summary(message, lang)
        elif state == ConversationState.HANDOVER:
            return await self._handle_handover(message, lang)
        else:
            return await self._handle_fallback(message, lang)

    async def _handle_greeting(self, lang: str):
        """Handle initial greeting and consent"""
        # Send greeting message
        greeting_text = self._get_localized_message("greeting", lang)
        await send_message(self.phone, greeting_text)

        # Move to consent stage
        await self.set_state(ConversationState.CONSENT)
        return {"stage": "greeting", "next": "consent"}

    async def _handle_consent(self, message: str, lang: str):
        """Handle consent collection"""
        consent_text = self._get_localized_message("consent", lang)
        await send_message(self.phone, consent_text)

        # For now, assume consent and move to language selection
        await self.set_state(ConversationState.LANGUAGE)
        return {"stage": "consent", "next": "language"}

    async def _handle_language_selection(self, message: str, lang: str):
        """Handle language preference"""
        # Store detected language preference
        self._memory_store[f"{self.state_key}:language"] = lang

        # Ask for legal matter type
        matter_text = self._get_localized_message("matter_type", lang)
        await send_message(self.phone, matter_text)

        await self.set_state(ConversationState.MATTER_TYPE)
        return {"stage": "language", "next": "matter_type"}

    async def _handle_matter_type(self, message: str, lang: str):
        """Handle legal matter type selection"""
        # Store matter type
        self._memory_store[f"{self.state_key}:matter_type"] = message

        # Ask for description
        desc_text = self._get_localized_message("description", lang)
        await send_message(self.phone, desc_text)

        await self.set_state(ConversationState.DESCRIPTION)
        return {"stage": "matter_type", "next": "description"}

    async def _handle_description(self, message: str, lang: str):
        """Handle case description"""
        # Store description
        self._memory_store[f"{self.state_key}:description"] = message

        # Ask for jurisdiction
        jurisdiction_text = self._get_localized_message("jurisdiction", lang)
        await send_message(self.phone, jurisdiction_text)

        await self.set_state(ConversationState.JURISDICTION)
        return {"stage": "description", "next": "jurisdiction"}

    async def _handle_jurisdiction(self, message: str, lang: str):
        """Handle jurisdiction information"""
        # Store jurisdiction
        self._memory_store[f"{self.state_key}:jurisdiction"] = message

        # Ask for document upload
        doc_text = self._get_localized_message("document_upload", lang)
        await send_message(self.phone, doc_text)

        await self.set_state(ConversationState.DOCUMENT_UPLOAD)
        return {"stage": "jurisdiction", "next": "document_upload"}

    async def _handle_document_upload(self, message: str, lang: str, media: dict = None):
        """Handle document upload"""
        # For now, just acknowledge and move to contact info
        contact_text = self._get_localized_message("contact_info", lang)
        await send_message(self.phone, contact_text)

        await self.set_state(ConversationState.CONTACT_INFO)
        return {"stage": "document_upload", "next": "contact_info"}

    async def _handle_contact_info(self, message: str, lang: str):
        """Handle contact information collection"""
        # Store contact info
        self._memory_store[f"{self.state_key}:contact_info"] = message

        # Show summary
        summary_text = self._get_localized_message("summary", lang)
        await send_message(self.phone, summary_text)

        await self.set_state(ConversationState.SUMMARY)
        return {"stage": "contact_info", "next": "summary"}

    async def _handle_summary(self, message: str, lang: str):
        """Handle case summary confirmation"""
        # Generate summary of collected information
        summary = self._generate_case_summary(lang)

        # Send summary to user
        await send_message(self.phone, summary)

        # Ask for confirmation
        confirm_text = self._get_localized_message("summary_confirm", lang)
        await send_message(self.phone, confirm_text)

        await self.set_state(ConversationState.HANDOVER)
        return {"stage": "summary", "next": "handover"}

    async def _handle_handover(self, message: str, lang: str):
        """Handle final handover to legal team"""
        handover_text = self._get_localized_message("handover", lang)
        await send_message(self.phone, handover_text)

        # Mark conversation as completed
        await self.set_state(ConversationState.GREETING)  # Reset for next interaction
        return {"stage": "handover", "status": "completed"}

    async def _handle_fallback(self, message: str, lang: str):
        """Handle unexpected messages"""
        fallback_text = self._get_localized_message("fallback", lang)
        await send_message(self.phone, fallback_text)
        return {"stage": "fallback"}

    def _get_localized_message(self, message_type: str, lang: str) -> str:
        """Get localized message based on language"""
        messages = {
            'en': {
                'greeting': "👋 Hello! I'm here to help you with your legal matter. I'll guide you through the process step by step.",
                'consent': "📋 Before we proceed, I need your consent to collect and process your information for legal consultation purposes. Do you agree to continue?",
                'language': "🌐 I detected you're communicating in English. Is this correct?",
                'matter_type': "⚖️ What type of legal matter do you need help with? (e.g., criminal, civil, family, corporate, etc.)",
                'description': "📝 Please describe your legal issue in detail. The more information you provide, the better I can assist you.",
                'jurisdiction': "🏛️ In which jurisdiction or court district is this matter located?",
                'document_upload': "📎 Do you have any documents related to this case? You can upload them now or we can proceed without them.",
                'contact_info': "📞 Please provide your full name and preferred contact method (email/phone) for follow-up.",
                'summary': "📋 Let me summarize what we've collected:",
                'summary_confirm': "✅ Does this summary look correct? Reply 'yes' to confirm or 'no' to make changes.",
                'handover': "🎯 Thank you! Your case has been submitted to our legal team. A lawyer will contact you within 24 hours.",
                'fallback': "🤔 I'm not sure I understood that. Could you please rephrase or start over?"
            },
            'es': {
                'greeting': "👋 ¡Hola! Estoy aquí para ayudarte con tu asunto legal. Te guiaré paso a paso a través del proceso.",
                'consent': "📋 Antes de proceder, necesito tu consentimiento para recopilar y procesar tu información con fines de consulta legal. ¿Estás de acuerdo en continuar?",
                'language': "🌐 Detecté que te comunicas en español. ¿Es correcto?",
                'matter_type': "⚖️ ¿Qué tipo de asunto legal necesitas ayuda? (ej: penal, civil, familiar, corporativo, etc.)",
                'description': "📝 Por favor describe tu problema legal en detalle. Cuanta más información proporciones, mejor podré ayudarte.",
                'jurisdiction': "🏛️ ¿En qué jurisdicción o distrito judicial se encuentra este asunto?",
                'document_upload': "📎 ¿Tienes documentos relacionados con este caso? Puedes subirlos ahora o podemos proceder sin ellos.",
                'contact_info': "📞 Por favor proporciona tu nombre completo y método de contacto preferido (email/teléfono) para seguimiento.",
                'summary': "📋 Permíteme resumir lo que hemos recopilado:",
                'summary_confirm': "✅ ¿Este resumen parece correcto? Responde 'sí' para confirmar o 'no' para hacer cambios.",
                'handover': "🎯 ¡Gracias! Tu caso ha sido enviado a nuestro equipo legal. Un abogado se pondrá en contacto contigo dentro de 24 horas.",
                'fallback': "🤔 No estoy seguro de haber entendido eso. ¿Podrías reformular o empezar de nuevo?"
            }
        }

        return messages.get(lang, messages['en']).get(message_type, messages['en'][message_type])

    def _generate_case_summary(self, lang: str) -> str:
        """Generate case summary from collected data"""
        matter_type = self._memory_store.get(f"{self.state_key}:matter_type", "Not specified")
        description = self._memory_store.get(f"{self.state_key}:description", "Not provided")
        jurisdiction = self._memory_store.get(f"{self.state_key}:jurisdiction", "Not specified")
        contact_info = self._memory_store.get(f"{self.state_key}:contact_info", "Not provided")

        summary_lines = [
            "📋 *Case Summary:*",
            f"⚖️ *Matter Type:* {matter_type}",
            f"📝 *Description:* {description[:200]}{'...' if len(description) > 200 else ''}",
            f"🏛️ *Jurisdiction:* {jurisdiction}",
            f"📞 *Contact Info:* {contact_info}"
        ]

        return "\n".join(summary_lines)