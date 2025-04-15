from datetime import datetime, UTC
from typing import Any

from sqlmodel import Session, select

from app.models import BatchJob, BatchTask, BatchStatus, Course, BatchJobCreate


def create_batch_job(
    *, session: Session, batch_in: BatchJobCreate | dict[str, Any], user_id: int
) -> BatchJob:
    """Create a new batch job and associated tasks"""
    # Convert dictionary to BatchJobCreate if needed
    if isinstance(batch_in, dict):
        batch_in = BatchJobCreate.model_validate(batch_in)

    batch_job = BatchJob(
        user_id=user_id, name=batch_in.name, total_tasks=len(batch_in.course_ids)
    )
    session.add(batch_job)
    session.flush()

    for course_id in batch_in.course_ids:
        task = BatchTask(batch_job_id=batch_job.id, course_id=course_id)
        session.add(task)

    session.commit()
    session.refresh(batch_job)
    return batch_job


def get_batch_job(
    *, session: Session, batch_job_id: int, user_id: int
) -> BatchJob | None:
    """Get a batch job by ID and verify user ownership"""
    statement = select(BatchJob).where(
        BatchJob.id == batch_job_id, BatchJob.user_id == user_id
    )
    return session.exec(statement).first()


def get_batch_jobs(*, session: Session, user_id: int) -> list[BatchJob]:
    """Get all batch jobs for a user"""
    statement = select(BatchJob).where(BatchJob.user_id == user_id)
    return session.exec(statement).all()


def get_batch_tasks(*, session: Session, batch_job_id: int) -> list[BatchTask]:
    """Get all tasks for a batch job"""
    statement = select(BatchTask).where(BatchTask.batch_job_id == batch_job_id)
    return session.exec(statement).all()


def update_batch_job_status(
    *, session: Session, batch_job_id: int, status: BatchStatus
) -> BatchJob | None:
    """Update the status of a batch job"""
    job = session.get(BatchJob, batch_job_id)
    if not job:
        return None

    job.status = status
    job.updated_at = datetime.now(UTC)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def update_task_status(
    *,
    session: Session,
    task_id: int,
    status: BatchStatus,
    result: str | None = None,
    error: str | None = None,
) -> BatchTask | None:
    """Update the status and potentially the result of a task"""
    task = session.get(BatchTask, task_id)
    if not task:
        return None

    task.status = status
    task.updated_at = datetime.now(UTC)

    if result is not None:
        task.result = result

    if error is not None:
        task.error = error

    session.add(task)
    session.commit()
    session.refresh(task)

    # Update the batch job completion count
    increment_completed_tasks(session=session, batch_job_id=task.batch_job_id)

    return task


def increment_completed_tasks(*, session: Session, batch_job_id: int) -> None:
    """Increment the completed_tasks counter for a batch job"""
    job = session.get(BatchJob, batch_job_id)
    if not job:
        return

    statement = select(BatchTask).where(
        BatchTask.batch_job_id == batch_job_id,
        BatchTask.status.in_([BatchStatus.COMPLETED, BatchStatus.FAILED]),
    )
    completed_count = len(session.exec(statement).all())

    job.completed_tasks = completed_count

    if job.completed_tasks >= job.total_tasks:
        job.status = BatchStatus.COMPLETED

    job.updated_at = datetime.now(UTC)
    session.add(job)
    session.commit()


def verify_course_ownership(*, session: Session, course_id: int, user_id: int) -> bool:
    """Verify that a course belongs to the specified user"""
    statement = select(Course).where(Course.id == course_id, Course.user_id == user_id)
    course = session.exec(statement).first()
    return course is not None
