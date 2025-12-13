import google.generativeai as genai
from typing import List, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure the Gemini API (will be configured when first used)
_api_configured = False

def _ensure_api_configured():
    """Ensure the Gemini API is configured."""
    global _api_configured
    if not _api_configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _api_configured = True

class GeminiClient:
    """Wrapper for Google's Gemini API client."""

    def __init__(self):
        _ensure_api_configured()
        self.model_name = settings.GEMINI_MODEL
        self._model = None
        self._embedding_model = None

    @property
    def model(self):
        """Lazy load the generative model when first accessed."""
        if self._model is None:
            self._model = genai.GenerativeModel(self.model_name)
        return self._model

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for the provided texts using Gemini.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        try:
            _ensure_api_configured()
            response = genai.embed_content(
                model="models/embedding-001",
                content=texts,
                task_type="retrieval_document"
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def generate_response(self, prompt: str, context: Optional[str] = None, system_instruction: Optional[str] = None) -> str:
        """
        Generate a response based on the prompt and optional context.

        Args:
            prompt: The user's query or prompt
            context: Optional context to ground the response in specific information
            system_instruction: Optional system instruction to guide the model's behavior

        Returns:
            Generated response text
        """
        try:
            if context:
                full_prompt = f"Based on the following context: {context}\n\nAnswer the question: {prompt}"
            else:
                full_prompt = prompt

            # Use a different model instance if system instruction is provided
            if system_instruction:
                model_with_instruction = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction
                )
                response = model_with_instruction.generate_content(full_prompt)
            else:
                response = self.model.generate_content(full_prompt)

            return response.text if response.text else ""
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            Embedding vector as a list of floats
        """
        try:
            _ensure_api_configured()
            response = genai.embed_content(
                model="models/embedding-001",
                content=[text],
                task_type="retrieval_document"
            )
            return response['embedding'][0]
        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            raise

# Global instance (will be created without immediate API calls)
gemini_client = GeminiClient()