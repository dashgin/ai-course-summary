from fastapi import FastAPI
from app.routers import auth, users, courses


app = FastAPI(
    title="AI Summary",
    description="AI-Powered Online Course Summary Generator",
    version="0.0.1",
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(users.router)
