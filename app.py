from fastapi import FastAPI, Request, HTTPException

from exceptions import UsernameAlreadyTakenError, FailedLoginError
from api.login_api import login_router
from api.feed_api import feed_router
from api.user_api import user_router


app = FastAPI(title='WASAPhoto Backend', openapi_url=None, docs_url=None, redoc_url=None)
app.include_router(login_router)
app.include_router(user_router)
app.include_router(feed_router)

@app.exception_handler(FailedLoginError)
async def failed_login(_: Request, __: FailedLoginError):
    raise HTTPException(status_code=403, detail='Login failed')

@app.exception_handler(UsernameAlreadyTakenError)
async def username_already_taken(_: Request, __: UsernameAlreadyTakenError):
    raise HTTPException(status_code=409, detail='Username already taken')
