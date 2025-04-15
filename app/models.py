from sqlmodel import SQLModel, Field, Column, TEXT
from datetime import datetime, UTC
from enum import Enum


class TokenPayload(SQLModel):
    sub: int


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# User model
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


# Course model
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


class CourseSummaryEdit(SQLModel):
    ai_summary: str
    finalize: bool = False


# Batch processing models
class BatchStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BatchJob(SQLModel, table=True):
    """A batch job represents a collection of tasks to be processed asynchronously"""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str = Field(max_length=255)
    status: BatchStatus = Field(default=BatchStatus.PENDING)
    total_tasks: int = Field(default=0)
    completed_tasks: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BatchTask(SQLModel, table=True):
    """A single task within a batch job"""

    id: int | None = Field(default=None, primary_key=True)
    batch_job_id: int = Field(foreign_key="batchjob.id")
    course_id: int = Field(foreign_key="course.id")
    status: BatchStatus = Field(default=BatchStatus.PENDING)
    result: str = Field(sa_column=Column(TEXT), default="")
    error: str = Field(sa_column=Column(TEXT), default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BatchJobCreate(SQLModel):
    """Payload for creating a new batch job"""

    name: str = Field(max_length=255)
    course_ids: list[int]


class BatchJobStatus(SQLModel):
    """Status response for a batch job"""

    id: int
    name: str
    status: BatchStatus
    total_tasks: int
    completed_tasks: int
    progress: float  # Calculated as completed_tasks / total_tasks
    created_at: datetime
    updated_at: datetime
