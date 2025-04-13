from typing import Any

from fastapi import APIRouter
from sqlmodel import select
from app.dependencies import CurrentUser, SessionDep
from app.models import CourseCreate, Course, CoursesPublic

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=Course)
def create_course(
    *, session: SessionDep, current_user: CurrentUser, course_in: CourseCreate
) -> Any:
    """
    Create new course.
    """
    course = Course.model_validate(course_in, update={"user_id": current_user.id})
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.get("/", response_model=CoursesPublic)
def get_courses(*, session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get all courses.
    """
    courses = session.exec(select(Course).where(Course.user_id == current_user.id))
    return CoursesPublic(courses=courses)
