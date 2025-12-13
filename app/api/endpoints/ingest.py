from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import logging

from app.models.document import DocumentIngestionRequest, DocumentIngestionResponse, DocumentMetadata
from app.services.ingestion_service import ingestion_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=DocumentIngestionResponse)
async def ingest_document(
    content: str = Form(..., description="Document content as text"),
    document_id: Optional[str] = Form(None, description="Optional document ID (auto-generated if not provided)"),
    file_name: Optional[str] = Form(None, description="Original file name"),
    file_type: Optional[str] = Form(None, description="File type (e.g., text/markdown)"),
    chunk_size: int = Form(1000, description="Number of tokens per chunk"),
    chunk_overlap: int = Form(200, description="Number of tokens to overlap between chunks")
):
    """
    Ingest a document into the RAG system.

    Args:
        content: Document content as text
        document_id: Optional document ID (auto-generated if not provided)
        file_name: Original file name
        file_type: File type (e.g., text/markdown)
        chunk_size: Number of tokens per chunk
        chunk_overlap: Number of tokens to overlap between chunks

    Returns:
        DocumentIngestionResponse with ingestion status
    """
    try:
        logger.info(f"Received ingestion request for document: {document_id or 'auto-generated'}")

        # Validate content
        if not content or not content.strip():
            raise HTTPException(
                status_code=400,
                detail="Document content cannot be empty"
            )

        # Validate chunk parameters
        if chunk_size <= 0 or chunk_size > 2000:
            raise HTTPException(
                status_code=400,
                detail="chunk_size must be between 1 and 2000"
            )

        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise HTTPException(
                status_code=400,
                detail="chunk_overlap must be between 0 and chunk_size-1"
            )

        # Prepare document metadata
        metadata = DocumentMetadata(
            source="api",
            file_name=file_name,
            file_size=len(content.encode('utf-8')),
            file_type=file_type
        )

        # Prepare ingestion request
        request = DocumentIngestionRequest(
            document_id=document_id,
            content=content,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Validate document content
        is_valid = ingestion_service.validate_document_content(content)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Document content is invalid (too large or empty)"
            )

        # Check if document already exists
        if document_id and ingestion_service.check_document_exists(document_id):
            raise HTTPException(
                status_code=409,
                detail=f"Document with ID {document_id} already exists"
            )

        # Ingest the document
        response = ingestion_service.ingest_document(request)

        logger.info(f"Successfully ingested document: {response.document_id}")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error during document ingestion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error ingesting document: {str(e)}"
        )


@router.post("/upload", response_model=DocumentIngestionResponse)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    document_id: Optional[str] = Form(None, description="Optional document ID (auto-generated if not provided)"),
    chunk_size: int = Form(1000, description="Number of tokens per chunk"),
    chunk_overlap: int = Form(200, description="Number of tokens to overlap between chunks")
):
    """
    Upload and ingest a document file into the RAG system.

    Args:
        file: Document file to upload
        document_id: Optional document ID (auto-generated if not provided)
        chunk_size: Number of tokens per chunk
        chunk_overlap: Number of tokens to overlap between chunks

    Returns:
        DocumentIngestionResponse with ingestion status
    """
    try:
        logger.info(f"Received file upload request: {file.filename}")

        # Validate file type
        allowed_extensions = {'.md', '.txt', '.markdown'}
        file_extension = '.' + file.filename.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )

        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')

        # Validate file size (max 10MB)
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="File size exceeds maximum allowed size of 10MB"
            )

        # Prepare document metadata
        metadata = DocumentMetadata(
            source="upload",
            file_name=file.filename,
            file_size=len(content),
            file_type=file.content_type
        )

        # Prepare ingestion request
        request = DocumentIngestionRequest(
            document_id=document_id,
            content=content_str,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Validate document content
        is_valid = ingestion_service.validate_document_content(content_str)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Document content is invalid (too large or empty)"
            )

        # Check if document already exists
        if document_id and ingestion_service.check_document_exists(document_id):
            raise HTTPException(
                status_code=409,
                detail=f"Document with ID {document_id} already exists"
            )

        # Ingest the document
        response = ingestion_service.ingest_document(request)

        logger.info(f"Successfully uploaded and ingested document: {response.document_id}")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except UnicodeDecodeError:
        logger.error(f"File {file.filename} is not a valid text file")
        raise HTTPException(
            status_code=400,
            detail="File is not a valid text file"
        )
    except Exception as e:
        logger.error(f"Error during file upload and ingestion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading and ingesting document: {str(e)}"
        )


@router.get("/status/{document_id}")
async def get_document_status(document_id: str):
    """
    Get the processing status of a document.

    Args:
        document_id: ID of the document to check

    Returns:
        Document status information
    """
    try:
        status = ingestion_service.get_document_status(document_id)
        return {
            "document_id": document_id,
            "status": status
        }
    except Exception as e:
        logger.error(f"Error getting document status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting document status: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the system.

    Args:
        document_id: ID of the document to delete

    Returns:
        Deletion status information
    """
    try:
        success = ingestion_service.delete_document(document_id)
        if success:
            return {
                "document_id": document_id,
                "deleted": True,
                "message": f"Document {document_id} successfully deleted"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )