"""AI Service handling Gemini model interaction and conversation logic."""
import asyncio
import base64
import logging
from typing import Optional
from app.core.config import settings
from app.core.security import EMOTIONAL_ASSISTANT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class AIService:
    """Service wrapping Google Gemini generative AI text interactions."""

    def __init__(self) -> None:
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None
        self._init_client()

    def _init_client(self) -> None:
        """Initialize Google GenAI client if API key is present."""
        if not self.api_key:
            logger.info("GEMINI_API_KEY is not set. AIService will run in guided setup mode.")
            return

        try:
            # pyrefly: ignore [missing-import]
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            logger.info(f"Google GenAI client initialized with model '{self.model_name}'.")
        except Exception as exc:
            logger.warning(f"Failed to initialize google-genai client: {exc}")
            try:
                # pyrefly: ignore [missing-import]
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key)
                self._client = legacy_genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=EMOTIONAL_ASSISTANT_SYSTEM_PROMPT,
                )
                logger.info("Configured legacy google.generativeai client as fallback.")
            except Exception as legacy_exc:
                logger.error(f"Failed to initialize any Gemini client: {legacy_exc}")
                self._client = None

    def is_configured(self) -> bool:
        """Return True if Gemini API key is configured."""
        return bool(self.api_key and self.api_key.strip())

    async def generate_response(
        self,
        prompt: str,
        conversation_history: Optional[list[dict[str, str]]] = None,
        context: Optional[str] = None,
        image_data: Optional[str] = None,
    ) -> str:
        """
        Generate an empathetic, grounded response from Gemini.
        Supports multi-turn memory, grounded context (RAG/Web), and image understanding.
        """
        if not self.is_configured():
            return (
                "👋 Hello! I am **SoulSync**, your Multi-Modal AI Personal Assistant.\n\n"
                "To unlock live intelligence powered by Google Gemini, please add your `GEMINI_API_KEY` to the `backend/.env` file and restart the backend server.\n\n"
                "Your chat session and database connectivity are fully operational!"
            )

        final_user_prompt = prompt
        if context:
            final_user_prompt = f"Grounded Context:\n{context}\n\nUser Question:\n{prompt}"

        try:
            # Modern google-genai client
            if hasattr(self._client, "models"):
                # pyrefly: ignore [missing-import]
                from google.genai import types

                contents = []
                if conversation_history:
                    for turn in conversation_history:
                        turn_text = (turn.get("content") or "").strip()
                        if not turn_text:
                            continue
                        role = "user" if turn.get("role") == "user" else "model"
                        contents.append(
                            types.Content(
                                role=role,
                                parts=[types.Part.from_text(text=turn_text)],
                            )
                        )

                # Multimodal prompt parts
                prompt_parts = [types.Part.from_text(text=final_user_prompt)]
                if image_data:
                    try:
                        if image_data.startswith("data:"):
                            header, b64_str = image_data.split(",", 1)
                            mime = header.split(";")[0].replace("data:", "")
                            img_bytes = base64.b64decode(b64_str)
                            prompt_parts.append(types.Part.from_bytes(data=img_bytes, mime_type=mime))
                        else:
                            img_bytes = base64.b64decode(image_data)
                            prompt_parts.append(types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"))
                    except Exception as img_err:
                        logger.warning(f"Failed to process attached image: {img_err}")

                contents.append(types.Content(role="user", parts=prompt_parts))

                config = types.GenerateContentConfig(
                    system_instruction=EMOTIONAL_ASSISTANT_SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=1500,
                )

                if hasattr(self._client, "aio") and hasattr(self._client.aio, "models"):
                    res = await self._client.aio.models.generate_content(
                        model=self.model_name,
                        contents=contents,
                        config=config,
                    )
                else:
                    res = await asyncio.to_thread(
                        self._client.models.generate_content,
                        model=self.model_name,
                        contents=contents,
                        config=config,
                    )

                return res.text or "I heard you, but I wasn't able to produce words for that just now."

            # Legacy google.generativeai client
            elif hasattr(self._client, "generate_content"):
                history_legacy = []
                if conversation_history:
                    for turn in conversation_history:
                        turn_text = (turn.get("content") or "").strip()
                        if not turn_text:
                            continue
                        role = "user" if turn.get("role") == "user" else "model"
                        history_legacy.append({"role": role, "parts": [turn_text]})

                if hasattr(self._client, "start_chat"):
                    chat = self._client.start_chat(history=history_legacy)
                    res = await asyncio.to_thread(chat.send_message, final_user_prompt)
                else:
                    res = await asyncio.to_thread(self._client.generate_content, final_user_prompt)

                return res.text or "I heard you, but I wasn't able to produce words for that just now."

            else:
                return (
                    "AI service is currently initializing or reconnecting. "
                    "Please verify that your Gemini API key is valid."
                )

        except Exception as exc:
            logger.error(f"Error during Gemini generation: {exc}")
            err_str = str(exc).lower()
            if "api key not valid" in err_str or "401" in err_str or "unauthenticated" in err_str:
                return "The configured Gemini API key appears to be invalid. Please check your `GEMINI_API_KEY` in `backend/.env`."
            elif "quota" in err_str or "429" in err_str:
                return "The Gemini API request limit has been reached. Please wait a moment before trying again."
            return "I encountered a temporary connection issue reaching the AI service. Please try again shortly."

    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate a 768-dimensional embedding vector for text using Gemini text-embedding-004.
        """
        if not self.is_configured() or not text.strip():
            return [0.0] * 768

        try:
            if hasattr(self._client, "models"):
                if hasattr(self._client, "aio") and hasattr(self._client.aio, "models"):
                    result = await self._client.aio.models.embed_content(
                        model=settings.EMBEDDING_MODEL,
                        contents=text,
                    )
                else:
                    result = await asyncio.to_thread(
                        self._client.models.embed_content,
                        model=settings.EMBEDDING_MODEL,
                        contents=text,
                    )
                if hasattr(result, "embedding") and hasattr(result.embedding, "values"):
                    return list(result.embedding.values)
                elif hasattr(result, "embeddings") and result.embeddings:
                    return list(result.embeddings[0].values)

            return [0.0] * 768
        except Exception as exc:
            logger.warning(f"Error generating embedding: {exc}")
            return [0.0] * 768

    def generate_title(self, prompt: str) -> str:
        """Generate a concise 3-6 word title for a conversation."""
        cleaned = " ".join(prompt.strip().split())
        words = cleaned.split()
        if len(words) <= 5:
            return cleaned.capitalize()
        return " ".join(words[:5]).capitalize() + "..."


ai_service = AIService()
