from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from typing import Dict, List

from app.models.embeddings import BatchEmbeddingRequest, EmbeddingJob, EmbeddingJobStatus, MarkdownProcessingRequest
from app.services.content_service import ContentService, get_content_service
from app.services.gemini_service import GeminiService, get_gemini_service
from app.core.rate_limiter import limiter, INGESTION_RATE_LIMIT, HEALTH_RATE_LIMIT

router = APIRouter()

# In-memory job storage (in production, use a database)
embedding_jobs: Dict[str, EmbeddingJob] = {}


@router.post("/embeddings/process", response_model=Dict)
@limiter.limit(INGESTION_RATE_LIMIT)
async def process_embeddings(
    request,
    request_body: BatchEmbeddingRequest,
    background_tasks: BackgroundTasks,
    content_service: ContentService = Depends(get_content_service)
):
    """Process markdown files and store embeddings in Qdrant"""
    try:
        # Create a job ID
        import uuid
        job_id = str(uuid.uuid4())

        # Create job record
        from datetime import datetime
        job = EmbeddingJob(
            job_id=job_id,
            status="pending",
            source_files=[req.source_file for req in request_body.texts if req.source_file],
            progress=0,
            total=len(request_body.texts),
            created_at=datetime.now()
        )
        embedding_jobs[job_id] = job

        # Update job status to processing
        job.status = "processing"
        embedding_jobs[job_id] = job

        # Process in background
        background_tasks.add_task(
            _process_embedding_job,
            job_id,
            request_body,
            content_service
        )

        return {
            "job_id": job_id,
            "status": "processing",
            "total_files": len(request_body.texts),
            "message": "Embedding job started successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start embedding job: {str(e)}"
        )


async def _process_embedding_job(
    job_id: str,
    request: BatchEmbeddingRequest,
    content_service: ContentService
):
    """Background task to process embedding job"""
    try:
        job = embedding_jobs.get(job_id)
        if not job:
            return

        processed_count = 0
        total_count = len(request.texts)

        for i, text_request in enumerate(request.texts):
            try:
                # Process the text
                content_ids = await content_service.process_raw_text(
                    text=text_request.text,
                    source_file=text_request.source_file or f"content_{i}.txt",
                    title=text_request.metadata.get("title", "")
                )

                processed_count += 1

                # Update job progress
                job.progress = processed_count
                embedding_jobs[job_id] = job
            except Exception as e:
                # Log error but continue processing other items
                print(f"Error processing text {i}: {str(e)}")
                continue

        # Mark job as completed
        job.status = "completed"
        job.completed_at = __import__('datetime').datetime.now()
        embedding_jobs[job_id] = job

    except Exception as e:
        # Mark job as failed
        job = embedding_jobs.get(job_id)
        if job:
            job.status = "failed"
            job.completed_at = __import__('datetime').datetime.now()
            embedding_jobs[job_id] = job


@router.post("/embeddings/process-markdown", response_model=Dict)
@limiter.limit(INGESTION_RATE_LIMIT)
async def process_markdown_files(
    request,
    markdown_request: MarkdownProcessingRequest,
    background_tasks: BackgroundTasks,
    content_service: ContentService = Depends(get_content_service)
):
    """Process markdown files from file paths and store embeddings in Qdrant"""
    try:
        source_files = markdown_request.source_files
        rebuild_collection = markdown_request.rebuild_collection

        # Additional validation
        if not source_files:
            raise HTTPException(
                status_code=400,
                detail="source_files list cannot be empty"
            )

        if len(source_files) > 100:  # Reasonable limit
            raise HTTPException(
                status_code=400,
                detail="Too many files, maximum 100 files per request"
            )

        # Validate file paths
        import os
        for file_path in source_files:
            if not file_path or len(file_path.strip()) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="File paths cannot be empty"
                )

            # Check for path traversal attacks
            if '..' in file_path or file_path.startswith('/'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file path: {file_path}"
                )

        # Create a job ID
        import uuid
        job_id = str(uuid.uuid4())

        # Create job record
        from datetime import datetime
        job = EmbeddingJob(
            job_id=job_id,
            status="pending",
            source_files=source_files,
            progress=0,
            total=len(source_files),
            created_at=datetime.now()
        )
        embedding_jobs[job_id] = job

        # Update job status to processing
        job.status = "processing"
        embedding_jobs[job_id] = job

        # If rebuild_collection is True, clear the collection first
        if rebuild_collection:
            from app.services.qdrant_service import get_qdrant_service
            qdrant_service = get_qdrant_service()
            await qdrant_service.clear_collection()

        # Process in background
        background_tasks.add_task(
            _process_markdown_job,
            job_id,
            source_files,
            content_service
        )

        return {
            "job_id": job_id,
            "status": "processing",
            "total_files": len(source_files),
            "message": "Markdown processing job started successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start markdown processing job: {str(e)}"
        )


async def _process_markdown_job(
    job_id: str,
    source_files: List[str],
    content_service: ContentService
):
    """Background task to process markdown files"""
    try:
        job = embedding_jobs.get(job_id)
        if not job:
            return

        processed_count = 0
        total_count = len(source_files)

        for i, file_path in enumerate(source_files):
            try:
                # Process the markdown file
                content_ids = await content_service.process_markdown_file(
                    file_path=file_path,
                    source_file=file_path.split('/')[-1]  # Get just the filename
                )

                processed_count += 1

                # Update job progress
                job.progress = processed_count
                embedding_jobs[job_id] = job
            except Exception as e:
                # Log error but continue processing other files
                print(f"Error processing file {file_path}: {str(e)}")
                continue

        # Mark job as completed
        job.status = "completed"
        job.completed_at = __import__('datetime').datetime.now()
        embedding_jobs[job_id] = job

    except Exception as e:
        # Mark job as failed
        job = embedding_jobs.get(job_id)
        if job:
            job.status = "failed"
            job.completed_at = __import__('datetime').datetime.now()
            embedding_jobs[job_id] = job


@router.get("/embeddings/job/{job_id}", response_model=EmbeddingJobStatus)
@limiter.limit(INGESTION_RATE_LIMIT)
async def get_embedding_job_status(
    request,
    job_id: str
):
    """Get the status of an embedding job"""
    job = embedding_jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )

    return EmbeddingJobStatus(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        total=job.total,
        message=f"Job is {job.status}",
        created_at=job.created_at,
        completed_at=job.completed_at
    )


@router.get("/embeddings/status")
@limiter.limit(HEALTH_RATE_LIMIT)
async def get_embeddings_status(
    request,
    content_service: ContentService = Depends(get_content_service)
):
    """Get the status of the embeddings service"""
    try:
        # Get collection status
        from app.services.qdrant_service import get_qdrant_service
        qdrant_service = get_qdrant_service()
        collection_status = await qdrant_service.get_collection_status()

        return {
            "status": "ok",
            "service": "embeddings",
            "collection_status": collection_status,
            "active_jobs": len([job for job in embedding_jobs.values() if job.status in ["pending", "processing"]]),
            "completed_jobs": len([job for job in embedding_jobs.values() if job.status == "completed"]),
            "failed_jobs": len([job for job in embedding_jobs.values() if job.status == "failed"])
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )


@router.get("/embeddings/jobs")
@limiter.limit(INGESTION_RATE_LIMIT)
async def list_embedding_jobs(
    request
):
    """List all embedding jobs"""
    return {
        "jobs": [
            EmbeddingJobStatus(
                job_id=job.job_id,
                status=job.status,
                progress=job.progress,
                total=job.total,
                message=f"Job is {job.status}",
                created_at=job.created_at,
                completed_at=job.completed_at
            ) for job in embedding_jobs.values()
        ],
        "total_jobs": len(embedding_jobs)
    }


@router.delete("/embeddings/job/{job_id}")
@limiter.limit(INGESTION_RATE_LIMIT)
async def cancel_embedding_job(
    request,
    job_id: str
):
    """Cancel an embedding job (in a real implementation, this would stop the processing)"""
    job = embedding_jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )

    # In a real implementation, we would cancel the background task
    # For now, we'll just mark it as failed
    job.status = "failed"
    job.completed_at = __import__('datetime').datetime.now()
    embedding_jobs[job_id] = job

    return {
        "message": f"Job {job_id} marked as cancelled",
        "job_id": job_id
    }