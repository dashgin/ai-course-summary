
from sqlmodel import Session, select
from app.models import Course, CourseCreate


def create_course(*, session: Session, course_in: CourseCreate) -> Course:
    db_course = Course.model_validate(course_in)
    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    return db_course


def get_course_by_id(*, session: Session, course_id: int) -> Course | None:
    statement = select(Course).where(Course.id == course_id)
    course = session.exec(statement).first()
    return course
