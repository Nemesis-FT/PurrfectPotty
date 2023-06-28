import bcrypt
import fastapi.routing
from fastapi import Depends
from data_proxy.backend.web.authentication import get_current_user
from data_proxy.backend.web.errors import Denied
from data_proxy.backend.web.models.read import UserRead
from data_proxy.backend.web.crud import *

router = fastapi.routing.APIRouter(
    prefix="/api/user/v1",
    tags=[
        "User v1",
    ],
)


@router.get("/me",
            summary="Get data about currently logged in user",
            status_code=200, response_model=UserRead)
def user_get(*, current_user=Depends(get_current_user)):
    return UserRead(username=current_user)
