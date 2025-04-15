from sqlmodel import Session, select
from app.models import Course, CourseCreate


def create_course(*, session: Session, course_in: CourseCreate, user_id: int) -> Course:
    db_course = Course.model_validate(course_in, update={"user_id": user_id})
    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    return db_course


def get_course_by_id(*, session: Session, course_id: int) -> Course | None:
    statement = select(Course).where(Course.id == course_id)
    course = session.exec(statement).first()
    return course


def update_course_with_summary(
    *, session: Session, course_id: int, ai_summary: str
) -> Course | None:
    """
    Update a course with an AI-generated summary and set status to completed.

    Args:
        session: Database session
        course_id: ID of the course to update
        ai_summary: The AI-generated summary

    Returns:
        The updated course or None if not found
    """
    course = get_course_by_id(session=session, course_id=course_id)
    if not course:
        return None

    course.ai_summary = ai_summary
    course.status = "completed"
    session.add(course)
    session.commit()
    session.refresh(course)
    return course
