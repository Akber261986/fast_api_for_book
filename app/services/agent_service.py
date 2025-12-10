from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

import google.generativeai as genai

from app.config.settings import settings
from app.core.exceptions import ContentProcessingError, InvalidContentError
from app.models.agents import ChatSession, Message
from app.services.content_service import ContentService, get_content_service
from app.services.gemini_service import get_gemini_service


class AgentService:
    """Service class for interacting with Google's Gemini agent capabilities"""

    def __init__(self, api_key: Optional[str] = None, content_service=None):
        if api_key is None:
            api_key = settings.gemini_api_key

        if not api_key:
            raise ValueError("GEMINI_API_KEY must be provided")

        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = "gemini-2.5-flash"  # Updated to current model for agent operations
        self.sessions: Dict[str, ChatSession] = {}  # In-memory session storage
        # Don't initialize content_service here to avoid circular dependency
        self.content_service = content_service
        self.gemini_service = get_gemini_service()

    async def query_with_context(self,
                                query: str,
                                context: List[Dict],
                                max_tokens: int = 500) -> str:
        """Process a query using the provided context"""
        try:
            # Format the context into a message
            context_text = "\n".join([
                f"Source: {item.get('source_file', 'Unknown')}\nContent: {item.get('text', '')}\nScore: {item.get('score', 0)}"
                for item in context
            ])

            system_message = f"""
            You are an AI assistant that answers questions based on provided book content.
            Use only the information in the context below to answer the user's question.
            If the answer is not in the provided context, say "I don't have enough information in the provided content to answer that question."
            Be concise and accurate in your responses.

            Context:
            {context_text}
            """

            # Use the Gemini model for generation
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                f"{system_message}\n\nUser Query: {query}",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3
                )
            )

            return response.text
        except Exception as e:
            raise Exception(f"Failed to process query with context: {str(e)}")

    async def generate_response_with_sources(self,
                                           query: str,
                                           context: List[Dict],
                                           max_tokens: int = 500) -> Dict:
        """Generate a response with source citations"""
        try:
            response_text = await self.query_with_context(query, context, max_tokens)

            # Extract source information
            sources = []
            for item in context:
                sources.append({
                    "content_id": item.get("id", ""),
                    "text": item.get("text", "")[:200] + "..." if len(item.get("text", "")) > 200 else item.get("text", ""),
                    "source_file": item.get("metadata", {}).get("source_file", ""),
                    "section": item.get("metadata", {}).get("section", ""),
                    "similarity_score": item.get("score", 0.0)
                })

            return {
                "response": response_text,
                "sources": sources
            }
        except Exception as e:
            raise Exception(f"Failed to generate response with sources: {str(e)}")

    async def validate_api_key(self) -> bool:
        """Validate that the API key is working"""
        try:
            # Try a simple operation to validate the API key
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                "Test",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=5
                )
            )
            return len(response.text) > 0
        except Exception:
            return False

    async def create_completion(self,
                              prompt: str,
                              context: Optional[str] = None,
                              max_tokens: int = 500) -> str:
        """Create a completion based on a prompt and optional context"""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"

            # Use the Gemini model for generation
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )

            return response.text
        except Exception as e:
            raise Exception(f"Failed to create completion: {str(e)}")

    # Chat Session Management Methods
    async def create_session(self, context: Optional[Dict[str, str]] = None) -> ChatSession:
        """Create a new chat session"""
        session_id = str(uuid4())
        now = datetime.now()

        session = ChatSession(
            session_id=session_id,
            messages=[],
            created_at=now,
            updated_at=now,
            context=context or {}
        )

        self.sessions[session_id] = session
        return session

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        return self.sessions.get(session_id)

    async def add_message_to_session(self, session_id: str, message: Message) -> ChatSession:
        """Add a message to a chat session"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Validate message count
        if len(session.messages) >= 100:
            raise ValueError("Session message limit reached (100 messages)")

        session.messages.append(message)
        session.updated_at = datetime.now()

        return session

    async def update_session_context(self, session_id: str, context: Dict[str, str]) -> ChatSession:
        """Update the context of a chat session"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.context.update(context)
        session.updated_at = datetime.now()

        return session

    async def get_conversation_context(self, session_id: str, context_window: int = 5) -> List[Dict]:
        """Get recent conversation context for a session"""
        session = self.sessions.get(session_id)
        if not session:
            return []

        # Get the most recent messages up to context_window
        recent_messages = session.messages[-context_window:]

        # Format as context for the LLM
        context_items = []
        for msg in recent_messages:
            context_items.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            })

        return context_items

    async def clear_session(self, session_id: str) -> bool:
        """Clear all messages from a session (but keep the session)"""
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.messages = []
        session.updated_at = datetime.now()
        return True

    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    # Conversation Processing Methods
    async def process_chat_query(self,
                                query: str,
                                session_id: Optional[str] = None,
                                context_window: int = 5,
                                max_tokens: int = 500) -> Dict:
        """Process a chat query with conversation context"""
        try:
            # Validate inputs
            if not query or len(query.strip()) == 0:
                raise ValueError("Query cannot be empty")

            if len(query) > 1000:
                raise ValueError("Query too long, must be under 1000 characters")

            if context_window < 1 or context_window > 20:
                raise ValueError("context_window must be between 1 and 20")

            if max_tokens < 1 or max_tokens > 2000:
                raise ValueError("max_tokens must be between 1 and 2000")

            # Create or get session
            if session_id:
                session = await self.get_session(session_id)
                if not session:
                    # If session doesn't exist, create a new one
                    session = await self.create_session()
                    session_id = session.session_id
            else:
                session = await self.create_session()
                session_id = session.session_id

            # Search for relevant content based on the query
            # If content_service was not passed during initialization, get it now
            if self.content_service is None:
                from app.services.content_service import get_content_service
                self.content_service = get_content_service()

            search_results = await self.content_service.search_content(
                query=query,
                top_k=5,
                similarity_threshold=0.6
            )

            # Get conversation context
            conversation_context = await self.get_conversation_context(session_id, context_window)

            # Format the context for the LLM
            context_text = "\n".join([
                f"{item['role']}: {item['content']}"
                for item in conversation_context
            ])

            # Create system message with both content context and conversation context
            full_context = f"""
            You are an AI assistant that answers questions based on provided book content.
            Use the book content below to answer the user's question.
            If the answer is not in the provided content, say "I don't have enough information in the provided content to answer that question."
            Be concise and accurate in your responses.

            Book Content Context:
            {self._format_search_results_for_context(search_results)}

            Conversation Context:
            {context_text}
            """

            # Add user message to session
            user_message = Message(
                message_id=str(uuid4()),
                role="user",
                content=query,
                timestamp=datetime.now(),
                sources=[]
            )
            await self.add_message_to_session(session_id, user_message)

            # Generate response using Gemini
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                f"{full_context}\n\nUser Query: {query}",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3
                )
            )

            response_text = response.text

            # Create assistant message with sources
            assistant_message = Message(
                message_id=str(uuid4()),
                role="assistant",
                content=response_text,
                timestamp=datetime.now(),
                sources=[{
                    "content_id": result["id"],
                    "text": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                    "source_file": result["source_file"],
                    "similarity_score": result["similarity_score"]
                } for result in search_results]
            )
            await self.add_message_to_session(session_id, assistant_message)

            return {
                "response": response_text,
                "sources": [{
                    "content_id": result["id"],
                    "text": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                    "source_file": result["source_file"],
                    "section": result["section"],
                    "similarity_score": result["similarity_score"]
                } for result in search_results],
                "session_id": session_id
            }
        except ValueError as ve:
            # Re-raise ValueError as is since it's a client error
            raise InvalidContentError(str(ve))
        except Exception as e:
            # Log the error (in a real app, you'd use proper logging)
            print(f"Process chat query error: {str(e)}")
            raise ContentProcessingError(f"Failed to process chat query: {str(e)}")

    def _format_search_results_for_context(self, search_results: List[Dict]) -> str:
        """Format search results for use as context in the LLM"""
        formatted_results = []
        for result in search_results:
            formatted_results.append(
                f"Source: {result['source_file']} | Section: {result['section']} | Score: {result['similarity_score']:.2f}\n"
                f"Content: {result['text'][:500]}{'...' if len(result['text']) > 500 else ''}\n"
            )
        return "\n".join(formatted_results)


# Global instance - this will be initialized when the app starts
agent_service = None


def get_agent_service() -> AgentService:
    """Get the global agent service instance"""
    global agent_service
    if agent_service is None:
        raise Exception("Agent service not initialized")
    return agent_service


def initialize_agent_service(api_key: Optional[str] = None) -> AgentService:
    """Initialize the agent service with the provided API key"""
    global agent_service
    # Don't pass content_service during initialization to avoid circular dependency
    agent_service = AgentService(api_key, content_service=None)
    return agent_service