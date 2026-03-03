# Backend

FastAPI-based backend for the Text-to-SQL application.

## Project Structure

- **api/** - API route handlers and endpoints
- **app/** - Application configuration and initialization
- **caches/** - Redis caching utilities
- **core/** - Core functionality (config, security)
- **db/** - Database models and connections (SQLAlchemy + asyncpg)
- **dspy/** - DSPy integration for LLM prompting
- **langchain/** - LangChain integration for text processing
- **models/** - Pydantic models and schemas
- **prompts/** - Prompt templates for LLM interactions
- **semantic_kernel/** - Microsoft Semantic Kernel integration
- **services/** - Business logic and external service integrations
- **tests/** - Test files and test utilities
- **utils/** - Helper functions and utilities

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Copy `.env.example` to `.env` and configure values

3. Run the server:
```bash
uv run uvicorn main:app --reload
```

## Key Technologies

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM (async with asyncpg)
- **Pydantic** - Data validation
- **LangChain / DSPy** - LLM integrations
