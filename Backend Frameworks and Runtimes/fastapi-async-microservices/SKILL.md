---
name: fastapi-async-microservices
metadata:
  category: Backend Frameworks and Runtimes
description: Design and develop production-grade asynchronous microservices using FastAPI, Python 3.12+, Pydantic v2 Settings and Schemas, SQLAlchemy 2.0 async sessions, dependency injection, lifespan state management, structured JSON logging, and connection pooling. Trigger when building async Python APIs, microservices, or high-concurrency backends.
compatibility: FastAPI 0.110+, Python 3.11+, SQLAlchemy 2.0+, Pydantic v2
---

# FastAPI Async Microservices Skill Guide

This skill establishes production architecture and coding standards for high-performance, asynchronous REST microservices built with FastAPI, Pydantic v2, and async SQLAlchemy.

---

## 1. Async Microservice Architecture

```text
[ Client HTTP Request ]
          |
          v
[ Uvicorn ASGI Server (uvloop) ]
          |
          v
[ FastAPI Application Pipeline ]
  |-- Lifespan Handler (DB pool startup / cleanup)
  |-- Global Middleware (CORS, Request-ID, Structured Logging)
  |-- Routers & Dependency Injection (Auth, DB AsyncSession, Rate-limiting)
          |
          +---> [ Pydantic v2 Validation & Deserialization ]
          |
          +---> [ Business Logic & Async SQLAlchemy 2.0 Engine ]
          |                  |
          |                  v (asyncpg connection pool)
          |           [ PostgreSQL 16+ ]
          |
          v
[ Structured JSON Response / RFC 7807 Error ]
```

---

## 2. Production Code Standards

### A. Environment Configuration (`config.py`)

```python
from functools import lru_cache
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "OrderService"
    ENV: str = "production"
    DEBUG: bool = False
    PORT: int = 8000

    # Database
    DATABASE_URL: PostgresDsn = "postgresql+asyncpg://user:secret@localhost:5432/orders_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### B. Database Session Lifecycle (`database.py`)

```python
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    # FastAPI Dependency providing request-scoped async database session
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### C. Schemas with Pydantic v2 (`schemas.py`)

```python
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    customer_id: UUID
    item_count: int = Field(gt=0, description="Item count must be greater than zero")
    total_amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class OrderResponse(BaseModel):
    id: UUID
    customer_id: UUID
    item_count: int
    total_amount: Decimal
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### D. Router Implementation (`router.py`)

```python
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models import Order
from app.schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])
DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, db: DbSession):
    order = Order(
        customer_id=payload.customer_id,
        item_count=payload.item_count,
        total_amount=payload.total_amount,
        status="PENDING",
    )
    db.add(order)
    await db.flush()
    await db.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: UUID, db: DbSession):
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    return order
```

### E. Lifespan & Application Setup (`main.py`)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine
from app.routers import orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    yield
    # Graceful shutdown: dispose of DB engine pool
    await engine.dispose()


settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.include_router(orders.router)


@app.get("/healthz", tags=["Ops"])
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}
```

---

## 3. Production Guidelines

1. **Session Scope:** Never reuse `AsyncSession` across concurrent coroutines; always use the `get_db_session` dependency.
2. **Explicit Flush:** Use `await db.flush()` rather than manual commits within repository logic to allow the dependency context to manage atomic commits/rollbacks.
3. **Disposal on Shutdown:** Always close the async engine in the FastAPI `lifespan` handler to prevent orphaned PostgreSQL backends.
