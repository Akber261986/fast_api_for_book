import asyncio
import json
from pathlib import Path

import httpx

# Test script to verify the RAG system is working

async def test_ingestion_and_query():
    """Test the complete RAG flow: ingest document and query it."""

    base_url = "http://localhost:8000"
    client = httpx.AsyncClient(timeout=30.0)

    try:
        # Test health check
        print("Testing health check...")
        response = await client.get(f"{base_url}/health")
        print(f"Health check: {response.status_code}, {response.json()}")

        # Test document ingestion
        print("\nTesting document ingestion...")

        # Create a test document
        test_doc_content = """
        # Introduction to AI
        Artificial Intelligence (AI) is a branch of computer science that aims to create software or machines that exhibit human-like intelligence.
        This can include learning from experience, understanding natural language, solving problems, and recognizing patterns.

        ## Types of AI
        There are several types of AI:
        - Narrow AI: Designed for specific tasks like voice recognition
        - General AI: Theoretical AI that can perform any intellectual task a human can do
        - Super AI: Hypothetical AI that surpasses human intelligence

        ## Machine Learning
        Machine Learning is a subset of AI that focuses on algorithms that can learn from data.
        """

        # Ingest the document
        response = await client.post(
            f"{base_url}/ingest/",
            data={
                "content": test_doc_content,
                "file_name": "test_ai_doc.md",
                "file_type": "text/markdown",
                "chunk_size": 1000,
                "chunk_overlap": 200
            }
        )
        print(f"Ingestion response: {response.status_code}")
        if response.status_code == 200:
            ingestion_result = response.json()
            print(f"Ingestion result: {json.dumps(ingestion_result, indent=2)}")
            doc_id = ingestion_result["document_id"]
        else:
            print(f"Ingestion error: {response.text}")
            return

        # Wait a moment for the document to be processed
        await asyncio.sleep(1)

        # Test querying
        print("\nTesting query functionality...")

        query_payload = {
            "query": "What are the types of AI mentioned in the document?",
            "top_k": 3,
            "similarity_threshold": 0.5
        }

        response = await client.post(
            f"{base_url}/query/",
            json=query_payload
        )
        print(f"Query response: {response.status_code}")
        if response.status_code == 200:
            query_result = response.json()
            print(f"Query result: {json.dumps(query_result, indent=2)}")
        else:
            print(f"Query error: {response.text}")

        # Test another query
        print("\nTesting another query...")
        query_payload2 = {
            "query": "What is Machine Learning according to the document?",
            "top_k": 3,
            "similarity_threshold": 0.5
        }

        response = await client.post(
            f"{base_url}/query/",
            json=query_payload2
        )
        print(f"Second query response: {response.status_code}")
        if response.status_code == 200:
            query_result2 = response.json()
            print(f"Second query result: {json.dumps(query_result2, indent=2)}")
        else:
            print(f"Second query error: {response.text}")

    except Exception as e:
        print(f"Test error: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    print("Starting RAG system test...")
    asyncio.run(test_ingestion_and_query())
    print("Test completed!")