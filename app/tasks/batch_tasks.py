import logging

from sqlmodel import Session

from app.celery_app import celery_app
from app.core.db import engine
from app.crud import batch
from app.models import BatchStatus, BatchTask, Course
from app.services.llm import OpenAILLMService
from app.core.config import settings


logger = logging.getLogger(__name__)


@celery_app.task(name="process_batch_job")
def process_batch_job(batch_job_id: int) -> str:
    """
    Process a batch job by scheduling individual tasks for each course

    Args:
        batch_job_id: The ID of the batch job to process

    Returns:
        str: Status message
    """
    logger.info(f"Processing batch job {batch_job_id}")

    with Session(engine) as session:
        batch.update_batch_job_status(
            session=session, batch_job_id=batch_job_id, status=BatchStatus.PROCESSING
        )

        tasks = batch.get_batch_tasks(session=session, batch_job_id=batch_job_id)

        for task in tasks:
            process_batch_task.delay(task.id)

    return f"Batch job {batch_job_id} processing started"


@celery_app.task(name="process_batch_task")
def process_batch_task(batch_task_id: int) -> str:
    """
    Process a single batch task

    Args:
        batch_task_id: The ID of the batch task to process

    Returns:
        str: Status message
    """
    logger.info(f"Processing batch task {batch_task_id}")

    try:
        with Session(engine) as session:
            task = session.get(BatchTask, batch_task_id)
            if not task:
                return f"Task {batch_task_id} not found"

            batch.update_task_status(
                session=session, task_id=batch_task_id, status=BatchStatus.PROCESSING
            )

            course = session.get(Course, task.course_id)
            if not course:
                error_msg = f"Course {task.course_id} not found"
                batch.update_task_status(
                    session=session,
                    task_id=batch_task_id,
                    status=BatchStatus.FAILED,
                    error=error_msg,
                )
                return error_msg

            llm_service = OpenAILLMService(api_key=settings.OPENAI_API_KEY)
            summary = llm_service.generate_course_summary(course.description)

            course.ai_summary = summary
            course.status = "draft"
            session.add(course)

            # Update he task as completed with the result
            batch.update_task_status(
                session=session,
                task_id=batch_task_id,
                status=BatchStatus.COMPLETED,
                result=summary,
            )

            session.commit()

        return f"Task {batch_task_id} processed successfully"

    except Exception as e:
        logger.exception(f"Error processing task {batch_task_id}: {str(e)}")

        with Session(engine) as session:
            batch.update_task_status(
                session=session,
                task_id=batch_task_id,
                status=BatchStatus.FAILED,
                error=str(e),
            )

        return f"Task {batch_task_id} failed: {str(e)}"


@celery_app.task(name="process_batch_courses")
def process_batch_courses(course_ids: list[int], job_name: str, user_id: int) -> str:
    """
    Create a batch job and process courses in batch

    Args:
        course_ids: list of course IDs to process
        job_name: Name of the batch job
        user_id: ID of the user who owns the courses

    Returns:
        str: Status message
    """
    logger.info(f"Creating batch job for {len(course_ids)} courses")

    with Session(engine) as session:
        for course_id in course_ids:
            if not batch.verify_course_ownership(
                session=session, course_id=course_id, user_id=user_id
            ):
                return f"Course {course_id} does not belong to user {user_id}"

        batch_job = batch.create_batch_job(
            session=session,
            batch_in={"name": job_name, "course_ids": course_ids},
            user_id=user_id,
        )

        process_batch_job.delay(batch_job.id)

        return f"Batch job {batch_job.id} created and scheduled"
