from sqlmodel import SQLModel, Field, func, DateTime, Column, TEXT
from datetime import datetime


class TokenPayload(SQLModel):
    sub: int

# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    email: str = Field(max_length=255, unique=True)
    is_superuser: bool = False


class UserCreate(SQLModel):
    name: str = Field(max_length=255)
    email: str = Field(max_length=255, unique=True)


class UserPublic(SQLModel):
    id: int
    name: str
    email: str


class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str = Field(max_length=255)
    description: str = Field(sa_column=Column(TEXT))
    ai_summary: str | None = Field(sa_column=Column(TEXT))
    status: str = Field(default="pending", max_length=50)
    created_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class CourseCreate(SQLModel):
    title: str = Field(max_length=255)
    description: str = Field(sa_column=Column(TEXT))


class CoursesPublic(SQLModel):
    courses: list[Course]
