from sqlmodel import SQLModel, Field, Column, TEXT
from datetime import datetime, UTC


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
    is_active: bool = Field(default=True)
    hashed_password: str


class UserCreate(SQLModel):
    name: str = Field(max_length=255)
    email: str = Field(max_length=255, unique=True)
    password: str


class UserPublic(SQLModel):
    id: int
    name: str
    email: str


class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str = Field(max_length=255)
    description: str = Field(sa_column=Column(TEXT))
    ai_summary: str = Field(sa_column=Column(TEXT), default="")
    status: str = Field(default="pending", max_length=50)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )


class CourseCreate(SQLModel):
    title: str = Field(max_length=255)
    description: str = Field(sa_column=Column(TEXT))


class CoursesPublic(SQLModel):
    courses: list[Course]
