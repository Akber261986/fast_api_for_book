from typing import List, Optional

import google.generativeai as genai

from app.config.settings import settings
from app.core.exceptions import EmbeddingGenerationError, InvalidContentError


class GeminiService:
    """Service class for interacting with Google's Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        if api_key is None:
            api_key = settings.gemini_api_key

        if not api_key:
            raise ValueError("GEMINI_API_KEY must be provided")

        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = settings.embedding_model

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            # Validate input
            if not text or len(text.strip()) == 0:
                raise ValueError("Text cannot be empty")

            if len(text) > 10000:  # Set reasonable limit
                raise ValueError("Text too long for embedding generation")

            # Generate embedding using the actual Gemini API
            result = genai.embed_content(
                model=self.model,
                content=[text],
                task_type="RETRIEVAL_DOCUMENT"  # Using document for content, query for search
            )

            if not result or 'embedding' not in result or len(result['embedding']) == 0:
                raise Exception("No embedding returned from API")

            return result['embedding'][0]  # Return the first embedding
        except ValueError as ve:
            raise InvalidContentError(str(ve))
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to generate embedding: {str(e)}")

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            # Validate inputs
            if not texts:
                raise ValueError("Texts list cannot be empty")

            if len(texts) > 100:  # Reasonable batch size limit
                raise ValueError("Batch size too large, maximum 100 texts per batch")

            # Process embeddings in batch
            results = []
            for i, text in enumerate(texts):
                try:
                    embedding = await self.generate_embedding(text)
                    results.append(embedding)
                except Exception as e:
                    raise Exception(f"Failed to generate embedding for text {i}: {str(e)}")
            return results
        except Exception as e:
            raise Exception(f"Failed to generate batch embeddings: {str(e)}")

    async def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using Gemini's generative capabilities"""
        try:
            model = genai.GenerativeModel('gemini-pro')  # Using generative model for text generation
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Failed to generate text: {str(e)}")

    async def validate_api_key(self) -> bool:
        """Validate that the API key is working"""
        try:
            # Try a simple operation to validate the API key
            result = genai.embed_content(
                model=self.model,
                content=["test"],
                task_type="RETRIEVAL_QUERY"
            )
            return len(result['embedding']) > 0
        except Exception:
            return False

    async def generate_embeddings_with_retry(self, texts: List[str], max_retries: int = 3) -> List[List[float]]:
        """Generate embeddings with retry logic for handling API rate limits"""
        for attempt in range(max_retries):
            try:
                return await self.batch_generate_embeddings(texts)
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e
                # Wait before retry (implementing exponential backoff)
                import asyncio
                await asyncio.sleep(2 ** attempt)  # Wait 1s, 2s, 4s for retries

        raise Exception(f"Failed to generate embeddings after {max_retries} attempts")

    async def get_embedding_dimensions(self) -> int:
        """Get the expected dimensions for embeddings from the model"""
        try:
            # Generate a test embedding to determine dimensions
            test_embedding = await self.generate_embedding("test")
            return len(test_embedding)
        except Exception as e:
            raise Exception(f"Failed to get embedding dimensions: {str(e)}")


# Global instance - this will be initialized when the app starts
gemini_service = None


def get_gemini_service() -> GeminiService:
    """Get the global Gemini service instance"""
    global gemini_service
    if gemini_service is None:
        raise Exception("Gemini service not initialized")
    return gemini_service


def initialize_gemini_service(api_key: Optional[str] = None) -> GeminiService:
    """Initialize the Gemini service with the provided API key"""
    global gemini_service
    gemini_service = GeminiService(api_key)
    return gemini_service