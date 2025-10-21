import re
from typing import Optional, Dict, List, Tuple
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class LanguageDetector:
    """
    Service for detecting the language of text messages.
    Supports multiple detection methods with fallbacks.
    """

    # Common language patterns for quick detection
    LANGUAGE_PATTERNS = {
        'en': [
            r'\b(the|and|or|but|in|on|at|to|for|of|with|by|is|are|was|were|be|been|have|has|had|do|does|did|will|would|could|should|may|might|must|can)\b',
            r'\b(hello|hi|hey|good|morning|afternoon|evening|night|thank|you|please|sorry|excuse|me|pardon)\b'
        ],
        'es': [
            r'\b(el|la|los|las|un|una|unos|unas|y|o|pero|en|con|por|para|desde|hasta|a|ante|bajo|cabe|con|contra|de|desde|durante|en|entre|hacia|hasta|mediante|para|por|según|sin|so|sobre|tras|versus|via)\b',
            r'\b(hola|gracias|por|favor|perdón|disculpa|buenos|días|tardes|noches|adiós|saludos)\b'
        ],
        'fr': [
            r'\b(le|la|les|un|une|des|et|ou|mais|dans|sur|à|pour|avec|par|est|sont|été|été|avoir|a|fait|faire|dire|pouvoir|vouloir|devoir|pouvoir|savoir|venir|aller|voir|parler|prendre|mettre|donner)\b',
            r'\b(bonjour|merci|s\'il|vous|plaît|pardon|excusez|bon|matin|après-midi|soir|bonsoir|au|revoir|salut)\b'
        ],
        'de': [
            r'\b(der|die|das|ein|eine|einer|eines|einem|einen|und|oder|aber|in|an|auf|zu|für|von|mit|bei|ist|sind|war|waren|sein|haben|hatte|können|müssen|dürfen|mögen|sollen|wollen)\b',
            r'\b(hallo|danke|bitte|entschuldigung|guten|morgen|tag|abend|nacht|tschüss|auf|wiedersehen|grüß)\b'
        ],
        'pt': [
            r'\b(o|a|os|as|um|uma|uns|umas|e|ou|mas|em|no|na|nos|nas|para|por|com|de|do|da|dos|das|ante|após|até|contra|desde|durante|entre|exceto|fora|mediante|perante|sem|sobre|sob)\b',
            r'\b(olá|obrigado|por|favor|desculpe|bom|dia|tarde|noite|adeus|até|logo|saudações)\b'
        ],
        'ar': [
            r'[\u0600-\u06FF]',  # Arabic Unicode range
            r'\b(مرحبا|شكرا|من|فضلك|عذرا|صباح|الخير|مساء|الخير|وداعا|تحية)\b'
        ],
        'hi': [
            r'[\u0900-\u097F]',  # Devanagari Unicode range (Hindi)
            r'\b(नमस्ते|धन्यवाद|कृपया|क्षमा|सुबह|शाम|अलविदा|नमस्कार)\b'
        ],
        'zh': [
            r'[\u4E00-\u9FFF]',  # Chinese Unicode range
            r'\b(你好|谢谢|请|对不起|早上|下午|晚上|再见|问候)\b'
        ]
    }

    # Language confidence thresholds
    CONFIDENCE_THRESHOLDS = {
        'high': 0.8,
        'medium': 0.6,
        'low': 0.4
    }

    def __init__(self):
        self.use_openai = bool(settings.openai_api_key)
        if self.use_openai:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
            except ImportError:
                logger.warning("OpenAI package not available, falling back to pattern matching")
                self.use_openai = False

    async def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        Returns ISO 639-1 language code (e.g., 'en', 'es', 'fr').
        """
        if not text or not text.strip():
            return 'en'  # Default to English for empty text

        text = text.strip()

        # Try OpenAI if available (most accurate)
        if self.use_openai:
            try:
                openai_result = await self._detect_with_openai(text)
                if openai_result and openai_result != 'unknown':
                    return openai_result
            except Exception as e:
                logger.warning(f"OpenAI language detection failed: {e}")

        # Fallback to pattern matching
        pattern_result = self._detect_with_patterns(text)
        if pattern_result:
            return pattern_result

        # Final fallback to English
        logger.info(f"Could not detect language for text: '{text[:50]}...', defaulting to 'en'")
        return 'en'

    async def _detect_with_openai(self, text: str) -> Optional[str]:
        """Detect language using OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a language detection expert. Respond with only the ISO 639-1 language code (2 letters) for the user's message. If unsure, respond with 'unknown'."
                    },
                    {
                        "role": "user",
                        "content": f"Detect the language of this text: {text[:500]}"
                    }
                ],
                max_tokens=10,
                temperature=0
            )

            detected_lang = response.choices[0].message.content.strip().lower()

            # Validate the response is a valid language code
            if len(detected_lang) == 2 and detected_lang in self.LANGUAGE_PATTERNS:
                return detected_lang
            elif detected_lang == 'unknown':
                return None

            logger.warning(f"OpenAI returned invalid language code: {detected_lang}")
            return None

        except Exception as e:
            logger.error(f"OpenAI language detection error: {e}")
            return None

    def _detect_with_patterns(self, text: str) -> Optional[str]:
        """Detect language using pattern matching"""
        scores = {}

        # Check each language's patterns
        for lang_code, patterns in self.LANGUAGE_PATTERNS.items():
            score = 0
            total_patterns = len(patterns)

            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE | re.UNICODE))
                if matches > 0:
                    # Weight different pattern types differently
                    if pattern.startswith(r'[\u'):  # Unicode range patterns
                        score += matches * 2  # Higher weight for character sets
                    else:
                        score += matches

            if score > 0:
                # Normalize score by text length and number of patterns
                normalized_score = score / (len(text) + 1) * (score / total_patterns)
                scores[lang_code] = normalized_score

        # Return language with highest score if above threshold
        if scores:
            best_lang = max(scores.items(), key=lambda x: x[1])
            if best_lang[1] >= self.CONFIDENCE_THRESHOLDS['low']:
                logger.info(f"Pattern detection: {best_lang[0]} with confidence {best_lang[1]:.3f}")
                return best_lang[0]

        return None

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        return list(self.LANGUAGE_PATTERNS.keys())

    def get_language_name(self, lang_code: str) -> str:
        """Get full language name from language code"""
        language_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'pt': 'Portuguese',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'zh': 'Chinese'
        }
        return language_names.get(lang_code, 'Unknown')

# Global language detector instance
language_detector = LanguageDetector()