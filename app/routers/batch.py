from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.crud import batch
from app.dependencies import CurrentUser, SessionDep
from app.models import BatchJob, BatchJobCreate, BatchJobStatus, BatchTask
from app.tasks.batch_tasks import process_batch_courses


router = APIRouter(prefix="/batch", tags=["batch"])


@router.post("/", response_model=BatchJob)
def create_batch_job(
    *, session: SessionDep, current_user: CurrentUser, batch_job_in: BatchJobCreate
) -> Any:
    """
    Create a new batch job.
    """
    for course_id in batch_job_in.course_ids:
        if not batch.verify_course_ownership(
            session=session, course_id=course_id, user_id=current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Course {course_id} does not belong to you",
            )

    batch_job = batch.create_batch_job(
        session=session, batch_in=batch_job_in, user_id=current_user.id
    )

    process_batch_courses.delay(
        course_ids=batch_job_in.course_ids,
        job_name=batch_job_in.name,
        user_id=current_user.id,
    )

    return batch_job


@router.get("/", response_model=list[BatchJobStatus])
def get_batch_jobs(*, session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get all batch jobs for the current user.
    """
    jobs = batch.get_batch_jobs(session=session, user_id=current_user.id)

    result = []
    for job in jobs:
        progress = job.completed_tasks / job.total_tasks if job.total_tasks > 0 else 0.0
        result.append(
            BatchJobStatus(
                id=job.id,
                name=job.name,
                status=job.status,
                total_tasks=job.total_tasks,
                completed_tasks=job.completed_tasks,
                progress=progress,
                created_at=job.created_at,
                updated_at=job.updated_at,
            )
        )

    return result


@router.get("/{batch_job_id}", response_model=BatchJobStatus)
def get_batch_job(
    *, session: SessionDep, current_user: CurrentUser, batch_job_id: int
) -> Any:
    """
    Get a batch job by ID.
    """
    job = batch.get_batch_job(
        session=session, batch_job_id=batch_job_id, user_id=current_user.id
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch job {batch_job_id} not found",
        )

    progress = job.completed_tasks / job.total_tasks if job.total_tasks > 0 else 0.0

    return BatchJobStatus(
        id=job.id,
        name=job.name,
        status=job.status,
        total_tasks=job.total_tasks,
        completed_tasks=job.completed_tasks,
        progress=progress,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/{batch_job_id}/tasks", response_model=list[BatchTask])
def get_batch_tasks(
    *, session: SessionDep, current_user: CurrentUser, batch_job_id: int
) -> Any:
    """
    Get all tasks for a batch job.
    """
    job = batch.get_batch_job(
        session=session, batch_job_id=batch_job_id, user_id=current_user.id
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch job {batch_job_id} not found",
        )

    tasks = batch.get_batch_tasks(session=session, batch_job_id=batch_job_id)
    return tasks
