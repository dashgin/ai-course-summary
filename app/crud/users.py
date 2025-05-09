from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models import User, UserCreate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_by_id(*, session: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    return user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user
