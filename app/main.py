from fastapi import FastAPI

app = FastAPI(
    title="AI Summary",
    description="AI-Powered Online Course Summary Generator",
    version="0.0.1",
)


@app.get("/")
async def root():
    return {"message": "Hello, World!"}
