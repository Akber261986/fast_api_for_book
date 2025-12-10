from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

from app.config.settings import settings
from app.core.exceptions import QdrantConnectionError


class QdrantDocument(BaseModel):
    """Model for documents stored in Qdrant"""
    id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, str]


class QdrantService:
    """Service class for interacting with Qdrant vector database"""

    def __init__(self, client: QdrantClient):
        self.client = client
        self.collection_name = settings.qdrant_collection_name

    async def initialize_collection(self) -> bool:
        """Initialize the collection if it doesn't exist"""
        try:
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.embedding_dimensions,
                        distance=Distance.COSINE
                    )
                )

            return True
        except Exception as e:
            print(f"Error initializing collection: {e}")
            return False

    async def store_embedding(self,
                            text: str,
                            embedding: List[float],
                            metadata: Optional[Dict] = None) -> str:
        """Store a single embedding in Qdrant"""
        if metadata is None:
            metadata = {}

        doc_id = str(uuid4())

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload={
                            "text": text,
                            **metadata
                        }
                    )
                ]
            )
            return doc_id
        except Exception as e:
            raise QdrantConnectionError(f"Failed to store embedding: {str(e)}")

    async def batch_store_embeddings(self,
                                   documents: List[QdrantDocument]) -> List[str]:
        """Store multiple embeddings in Qdrant"""
        try:
            points = []
            doc_ids = []

            for doc in documents:
                doc_id = doc.id or str(uuid4())
                doc_ids.append(doc_id)

                points.append(
                    models.PointStruct(
                        id=doc_id,
                        vector=doc.embedding,
                        payload={
                            "text": doc.text,
                            **doc.metadata
                        }
                    )
                )

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            return doc_ids
        except Exception as e:
            raise QdrantConnectionError(f"Failed to batch store embeddings: {str(e)}")

    async def search_similar(self,
                           query_embedding: List[float],
                           top_k: int = 5,
                           similarity_threshold: float = 0.7,
                           filters: Optional[Dict] = None) -> List[Dict]:
        """Search for similar embeddings in Qdrant"""
        try:
            # Prepare filters if provided
            search_filter = None
            if filters:
                must_conditions = []
                for key, value in filters.items():
                    must_conditions.append(
                        models.FieldCondition(
                            key=f"metadata.{key}",
                            match=models.MatchValue(value=value)
                        )
                    )
                if must_conditions:
                    search_filter = models.Filter(must=must_conditions)

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=similarity_threshold,
                query_filter=search_filter
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "text": result.payload.get("text", ""),
                    "score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"}
                })

            return formatted_results
        except Exception as e:
            raise QdrantConnectionError(f"Search failed: {str(e)}")

    async def get_document_by_id(self, doc_id: str) -> Optional[Dict]:
        """Retrieve a document by its ID"""
        try:
            records = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[doc_id]
            )

            if records:
                record = records[0]
                return {
                    "id": record.id,
                    "text": record.payload.get("text", ""),
                    "metadata": {k: v for k, v in record.payload.items() if k != "text"}
                }

            return None
        except Exception as e:
            raise QdrantConnectionError(f"Failed to retrieve document: {str(e)}")

    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document by its ID"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[doc_id]
                )
            )
            return True
        except Exception as e:
            raise QdrantConnectionError(f"Failed to delete document: {str(e)}")

    async def get_collection_status(self) -> Dict:
        """Get status information about the collection"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params.vectors_count,
                "vectors_count": collection_info.points_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "status": collection_info.status
            }
        except Exception as e:
            raise QdrantConnectionError(f"Failed to get collection status: {str(e)}")

    async def clear_collection(self) -> bool:
        """Clear all points from the collection"""
        try:
            # Get all point IDs
            all_points = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000  # Adjust based on expected collection size
            )[0]

            point_ids = [point.id for point in all_points]

            if point_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(
                        points=point_ids
                    )
                )

            return True
        except Exception as e:
            raise QdrantConnectionError(f"Failed to clear collection: {str(e)}")


# Global instance - this will be initialized when the app starts
qdrant_service = None


def get_qdrant_service() -> QdrantService:
    """Get the global Qdrant service instance"""
    global qdrant_service
    if qdrant_service is None:
        raise Exception("Qdrant service not initialized")
    return qdrant_service


def initialize_qdrant_service() -> QdrantService:
    """Initialize the Qdrant service with the provided client"""
    global qdrant_service
    from app.config.settings import settings
    from qdrant_client import QdrantClient
    import urllib.parse

    # Check if the host is a full URL (contains protocol)
    if settings.qdrant_host.startswith(('http://', 'https://')):
        # If it's a full URL, use the url parameter instead of host
        client = QdrantClient(
            url=settings.qdrant_host,
            api_key=settings.qdrant_api_key,
        )
    else:
        # Use traditional host/port configuration
        if settings.qdrant_api_key:
            client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key,
                https=settings.qdrant_https,
            )
        else:
            client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                https=settings.qdrant_https,
            )

    qdrant_service = QdrantService(client)
    return qdrant_service