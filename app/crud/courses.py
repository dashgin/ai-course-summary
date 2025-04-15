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
    *, session: Session, course_id: int, ai_summary: str, finalize: bool = False
) -> Course | None:
    """
    Update a course with an AI-generated summary.

    Args:
        session: Database session
        course_id: ID of the course to update
        ai_summary: The AI-generated summary
        finalize: If True, set status to completed; otherwise, set to draft

    Returns:
        The updated course or None if not found
    """
    course = get_course_by_id(session=session, course_id=course_id)
    if not course:
        return None

    course.ai_summary = ai_summary
    course.status = "completed" if finalize else "draft"
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


def finalize_course_summary(
    *, session: Session, course_id: int, ai_summary: str = None
) -> Course | None:
    """
    Finalize a course summary, optionally updating the AI summary.

    Args:
        session: Database session
        course_id: ID of the course to update
        ai_summary: Optional updated AI summary

    Returns:
        The updated course or None if not found
    """
    course = get_course_by_id(session=session, course_id=course_id)
    if not course:
        return None

    if ai_summary is not None:
        course.ai_summary = ai_summary
    
    course.status = "completed"
    session.add(course)
    session.commit()
    session.refresh(course)
    return course
