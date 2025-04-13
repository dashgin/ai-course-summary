from sqlmodel import SQLModel, Field, func, DateTime, Column, TEXT
from datetime import datetime


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    email: str = Field(max_length=255, unique=True)


class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    course_title: str = Field(max_length=255)
    course_description: str = Field(sa_column=Column(TEXT))
    ai_summary: str | None = Field(sa_column=Column(TEXT))
    status: str = Field(default="pending", max_length=50)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
