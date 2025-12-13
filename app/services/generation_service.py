from typing import List, Dict, Any
import logging
from uuid import uuid4
from datetime import datetime

from app.core.gemini_client import gemini_client
from app.models.query import QueryResponse, QueryChunk

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for generating responses using Gemini based on retrieved context."""

    def __init__(self):
        pass

    def generate_response(self, query: str, context: str = None, source_chunks: List[Dict[str, Any]] = None) -> QueryResponse:
        """
        Generate a response based on the query and optional context.
        The response will be constrained to only include information from the provided context.

        Args:
            query: The user's query
            context: Optional context to ground the response in specific information
            source_chunks: List of source chunks used to generate the response

        Returns:
            QueryResponse containing the generated answer and metadata
        """
        try:
            # Validate inputs
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")

            # If context is provided, generate response constrained to that context
            if context:
                # Create a prompt that explicitly asks the model to only use the provided context
                constrained_answer = gemini_client.generate_response(
                    query,
                    context,
                    system_instruction="You are a helpful assistant that only responds based on the provided context. Only use information that is explicitly mentioned in the context. If the context does not contain information to answer the query, respond with 'I cannot answer this question based on the provided documents.'"
                )

                # Validate that the response is grounded in the context
                is_valid = self.validate_response(constrained_answer, context)

                # If the response is not well-grounded in context, use a fallback approach
                if not is_valid and len(context.strip()) > 0:
                    logger.warning(f"Response not well-grounded in context for query: {query[:50]}...")
                    # Try again with stricter instructions
                    constrained_answer = gemini_client.generate_response(
                        query,
                        context,
                        system_instruction="You are a helpful assistant. Only use information that is explicitly mentioned in the provided context. Do not make up any information. If the context does not contain enough information to answer the query, say exactly 'I cannot answer this question based on the provided documents.'"
                    )

                answer = constrained_answer
            else:
                # If no context is provided, the model should indicate that
                answer = gemini_client.generate_response(
                    query,
                    context,
                    system_instruction="You are a helpful assistant. If asked about specific documents or content, inform the user that no documents were provided to answer their question."
                )

            # Calculate confidence based on context relevance and validation
            confidence = self._calculate_confidence(answer, context, query)

            # Prepare source chunks for response
            formatted_source_chunks = []
            if source_chunks:
                for chunk in source_chunks:
                    formatted_source_chunks.append({
                        'chunk_id': chunk.get('chunk_id', ''),
                        'document_id': chunk.get('document_id', ''),
                        'content': chunk.get('content', ''),
                        'score': chunk.get('score', 0.0)
                    })

            # Create response object
            response = QueryResponse(
                response_id=str(uuid4()),
                query=query,
                answer=answer,
                source_chunks=formatted_source_chunks,
                confidence=confidence,
                timestamp=datetime.now()
            )

            logger.info(f"Generated response for query: {query[:50]}...")
            return response

        except ValueError as ve:
            logger.error(f"Invalid input for response generation: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def _calculate_confidence(self, answer: str, context: str, query: str) -> float:
        """
        Calculate a confidence score for the generated response.
        This is a simplified approach - in a real implementation,
        this would use more sophisticated methods.

        Args:
            answer: The generated answer
            context: The context used for generation
            query: The original query

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not context:
            # If no context was provided, confidence is lower
            return 0.5

        # Simple heuristic: if the answer contains information from the context,
        # we have higher confidence
        answer_lower = answer.lower()
        context_lower = context.lower()

        # Count how many words from context appear in the answer
        context_words = set(context_lower.split())
        answer_words = set(answer_lower.split())

        if context_words:
            overlap = len(context_words.intersection(answer_words))
            overlap_ratio = overlap / len(context_words)
            # Base confidence on overlap, but cap it to avoid overconfidence
            confidence = min(0.8, 0.3 + (overlap_ratio * 0.7))
        else:
            confidence = 0.5

        return confidence

    def validate_response(self, response: str, context: str) -> bool:
        """
        Validate that the response is grounded in the provided context.
        This is a basic implementation - a full implementation would use more sophisticated validation.

        Args:
            response: The generated response
            context: The context used for generation

        Returns:
            True if response appears to be grounded in context, False otherwise
        """
        if not context:
            return True  # Can't validate without context

        response_lower = response.lower()
        context_lower = context.lower()

        # Check if response contains information that appears in context
        response_sentences = response_lower.split('.')
        context_words = set(context_lower.split())

        for sentence in response_sentences:
            sentence_words = set(sentence.split())
            # If sentence has significant overlap with context, it's likely grounded
            if len(sentence_words.intersection(context_words)) > 1:  # At least 2 common words
                return True

        # If no clear grounding found, return False
        return False


# Global instance
generation_service = GenerationService()