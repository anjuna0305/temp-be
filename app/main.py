from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

from app.auth.auth_router import router as auth_router
from app.router.user_router import router as user_router
from app.router.admin_router import router as admin_router
from app.router.test_router import router as test_router

from app.config.database.postgres_config import async_engine
from app.model.db_model import Base

from app.config.database.postgres_config import AsyncSessionLocal
from app.model.db_enum import UserRole
from app.model.db_model import User


app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:*",
    "http://vh2.local",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create the database tables on startup
@app.on_event("startup")
async def init_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    user = User(
        username="admin",
        hashed_password="$2b$12$96axD49e8FMatkcr.9oYouOt.Z7UKFoRmv.ZxlYo4pFJHV8FWcW8y",
        email="admin@email.com",
        scopes=UserRole.ADMIN,
    )

    async with AsyncSessionLocal() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(test_router, prefix="/test", tags=["test"])
