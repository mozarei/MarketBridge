from celery.result import AsyncResult
from fastapi import APIRouter

from app.schemas.jobs import JobStatusResponse
from app.tasks.celery_app import celery_app

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    result = AsyncResult(job_id, app=celery_app)
    successful = result.successful() if result.ready() else None
    error = str(result.result) if result.failed() else None

    response = JobStatusResponse(
        job_id=job_id,
        state=result.state,
        ready=result.ready(),
        successful=successful,
        result=result.result if result.ready() and successful else None,
        error=error,
    )
    return response
