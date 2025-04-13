from app.core.security import verify_password
from app.models import User
from .users import get_user_by_email
from sqlmodel import Session, select


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
