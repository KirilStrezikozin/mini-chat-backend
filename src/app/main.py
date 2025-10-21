from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine

from app.api import api_v1_router
from app.core.config import config
from app.utils.middleware import AuthenticationMiddleware
from app.utils.s3 import create_s3_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine(config.database.uri)
    app.state.engine = engine

    s3_client = create_s3_client(config)
    app.state.s3_client = s3_client

    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    AuthenticationMiddleware,
    config=config,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=config.PREFIX_API_V1)
