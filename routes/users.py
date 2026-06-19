from fastapi import (
    APIRouter,
    Depends,
    Request,
    UploadFile,
    File
)

from sqlalchemy.orm import Session

from slowapi import Limiter
from slowapi.util import get_remote_address

from models import User
from schemas import UserResponse
from services.auth import get_current_user
from services.cloudinary_service import upload_avatar
from database import get_db

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


@router.patch(
    "/avatar",
    response_model=UserResponse
)
def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    avatar_url = upload_avatar(
        file.file
    )

    current_user.avatar = avatar_url

    db.commit()
    db.refresh(current_user)

    return current_user
