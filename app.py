from fastapi import FastAPI

from api.login_api import login_router
from api.feed_api import feed_router
from api.user_api import user_router


app = FastAPI(title='WASAPhoto Backend', openapi_url=None, docs_url=None, redoc_url=None)
app.include_router(login_router)
app.include_router(user_router)
app.include_router(feed_router)
