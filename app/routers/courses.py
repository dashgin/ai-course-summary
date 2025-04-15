from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.dependencies import CurrentUser, SessionDep, OpenAILLMServiceDep
from app.models import CourseCreate, Course, CoursesPublic
from app.crud import courses as courses_crud

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=Course)
def create_course(
    *, session: SessionDep, current_user: CurrentUser, course_in: CourseCreate
) -> Any:
    """
    Create new course.
    """
    course = courses_crud.create_course(
        session=session, course_in=course_in, user_id=current_user.id
    )
    return course


@router.get("/", response_model=CoursesPublic)
def get_courses(*, session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get all courses.
    """
    courses = session.exec(select(Course).where(Course.user_id == current_user.id))
    return CoursesPublic(courses=courses)


@router.post("/generate_summary/{course_id}", response_model=Course)
def generate_summary(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    course_id: int,
    llm_service: OpenAILLMServiceDep,
) -> Course:
    """
    Generate an AI summary for a course.

    This endpoint:
    1. Fetches the course description from the database
    2. Calls OpenAI's GPT API to generate a short summary
    3. Stores the AI-generated summary in the database
    4. Updates the status to "completed"
    5. Returns the summarized course description
    """
    # Get the course from the database
    course = courses_crud.get_course_by_id(session=session, course_id=course_id)

    # Check if the course exists
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found",
        )

    # Check if the user owns the course
    if course.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this course",
        )

    # Generate the summary using OpenAI
    summary = llm_service.generate_course_summary(course.description)

    # Update the course with the summary
    updated_course = courses_crud.update_course_with_summary(
        session=session, course_id=course_id, ai_summary=summary
    )

    if not updated_course:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update course with summary",
        )

    return updated_course
