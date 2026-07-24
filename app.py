from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from providers.rate_limiting import liveness_limiter
from providers.redis import connect_redis_from_env
from providers.minio import connect_minio_from_env
from providers.db import get_engine_from_env
from db.engine import get_sessionmaker

from api.login_api import login_router
from api.feed_api import feed_router
from api.user_api import user_router
from exceptions import AppError


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_engine = get_engine_from_env()
    app.state.sessionmaker = get_sessionmaker(app.state.db_engine)
    app.state.redis = await connect_redis_from_env()
    app.state.minio = connect_minio_from_env()

    yield

    await app.state.redis.aclose()
    await app.state.db_engine.dispose()


app = FastAPI(title='WASNTAPhoto Backend', lifespan=lifespan, openapi_url=None, docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],    # nosemgrep: python.fastapi.security.wildcard-cors.wildcard-cors -- VERY bad in prod, but this is a demo, see comment below
    #allow_origins=['https://wasntaphoto.com/'],
    allow_credentials=True,
    allow_methods=['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS'],
    allow_headers=['Accept', 'Authorization', 'Content-Type'],
)

app.include_router(login_router)
app.include_router(user_router)
app.include_router(feed_router)


@app.get('/liveness', dependencies=[Depends(liveness_limiter)])
async def liveness() -> JSONResponse:
    return JSONResponse({'status': 'healthy'}, status_code=status.HTTP_200_OK)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})
