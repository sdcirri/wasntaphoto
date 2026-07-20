from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from providers.redis import connect_redis, disconnect_redis
from providers.rate_limiting import liveness_limiter
from api.login_api import login_router
from api.feed_api import feed_router
from api.user_api import user_router
from exceptions import AppError


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_redis()
    yield
    await disconnect_redis()


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
