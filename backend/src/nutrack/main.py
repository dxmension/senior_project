import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

from nutrack.router import api_router
from nutrack.config import settings
from nutrack.exceptions import AppException
from nutrack.handlers import app_exception_handler
from nutrack.redis import close_redis, init_redis
from nutrack.scheduler import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    scheduler.start()
    
    yield
    
    scheduler.shutdown(wait=False)
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(api_router)
