from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserResponse
from app.dependencies.auth import get_current_user
from app.models.user import UserModel
from app.db.database import get_db
from app.core.exceptions import create_response
from app.dependencies.auth import get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def read_current_user(
    request: Request, current_user: UserModel = Depends(get_current_user)
):
    """Lấy thông tin user hiện tại."""

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy thông tin người dùng thành công",
        data=UserResponse.model_validate(current_user),
        path=request.url.path,
    )


# GET /users
@router.get("")
def get_users(
    request: Request,
    search: str | None,
    is_active: bool | None,
    admin: UserModel = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Admin lấy danh sách user, ko lấy tài khoản ADMIN"""
    query = db.query(UserModel).filter(UserModel.role != "ADMIN")
    # Search theo tên hoặc email
    if search:
        keyword = f"%{search}%"
        query = query.filter(
            (UserModel.full_name.ilike(keyword)) | (UserModel.email.ilike(keyword))
        )
    # Lọc theo trạng thái
    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)
    users = query.all()
    data = [UserResponse.model_validate(user) for user in users]
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách người dùng thành công",
        data=data,
        path=request.url.path,
    )

