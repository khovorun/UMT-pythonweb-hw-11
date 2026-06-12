from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from models import User
from schemas import UserResponse
from services.auth import get_current_user

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/me",
    response_model=UserResponse
)
@limiter.limit("5/minute")
def read_users_me(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return current_user
