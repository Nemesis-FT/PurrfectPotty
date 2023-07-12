import pathlib

import fastapi
import pkg_resources
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.exceptions import HTTPException

from data_proxy.backend.web.authentication import authenticate_user, create_token, Token
from data_proxy.backend.web.errors import ApplicationException

from data_proxy.backend.web.routes.api.user.v1.router import router as user_router
from data_proxy.backend.web.routes.api.settings.v1.router import router as settings_router
from data_proxy.backend.web.routes.api.actions.v1.router import router as action_router

from handlers import handle_generic_error, handle_application_error

with open(pathlib.Path(__file__).parent.joinpath("description.md")) as file:
    description = file.read()

app = fastapi.FastAPI(
    debug=False,
    title="Data Proxy",
    description=description,
    version="0.1",
)

app.include_router(user_router)
app.include_router(settings_router)
app.include_router(action_router)

app.add_exception_handler(ApplicationException, handle_application_error)
app.add_exception_handler(Exception, handle_generic_error)


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Funzione di autenticazione. Se le credenziali sono corrette viene restituito un JWT
    :param form_data: informazioni di autenticazione
    :return: un dict contenente il token e il suo tipo
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    token = create_token(data={"sub": "admin"})
    return {"access_token": token, "token_type": "bearer"}