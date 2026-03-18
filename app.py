from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from exceptions import AppError
from api.login_api import login_router
from api.feed_api import feed_router
from api.user_api import user_router


app = FastAPI(title='WASNTAPhoto Backend', openapi_url=None, docs_url=None, redoc_url=None)
app.include_router(login_router)
app.include_router(user_router)
app.include_router(feed_router)

@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})
