# AI Course Summary Generator

A FastAPI service that leverages OpenAI to generate concise summaries of online courses.

## Overview

This service allows users to store course information and generate AI-powered summaries. It's built with a modern tech stack and provides a RESTful API for easy integration.

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Async Processing**: Celery with Redis
- **AI Integration**: OpenAI API
- **Containerization**: Docker
- **Authentication**: JWT-based auth system

## Features

- Complete user management system (signup, login, profile)
- Course creation and storage
- Background processing for AI summary generation
- Robust API with documentation
- Containerized deployment for easy setup

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Environment Setup

Create a `.env` file in the project root with the following variables:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_SERVER=postgres
REDIS_HOST=redis
REDIS_PORT=6379
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
```

> **Important**: Replace `your_openai_api_key` with your actual OpenAI API key and generate a secure `SECRET_KEY` for JWT authentication.

### Running the Application

```bash
# Clone the repository
git clone https://github.com/dashgin/ai-course-summary.git
cd ai-course-summary

# Start the application
docker compose up -d
```

The API will be available at `http://localhost:8000`.
API documentation is available at `http://localhost:8000/docs`.

## API Endpoints

### Authentication
- `POST /auth/token` - Get JWT token (login)

### Users
- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get user details
- `PUT /users/{user_id}` - Update user

### Courses
- `POST /courses` - Create a new course
- `GET /courses` - List all courses
- `GET /courses/{course_id}` - Get course details
- `POST /generate_summary/{course_id}` - Request summary generation
- `GET /batch/{task_id}` - Check status of summary generation

## Development

To run the application in development mode with hot-reload:

```bash
docker compose up -d
```

Changes to the `app` directory will be synchronized to the container automatically.

