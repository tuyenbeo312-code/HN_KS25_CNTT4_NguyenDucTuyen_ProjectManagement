from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth_schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
)
from app.schemas.user_schema import UserResponse
from app.services.auth_services import register_user, login_user
from app.core.exceptions import create_response

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# Đăng ký tài khoản
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản",
    description=("""Đăng ký một tài khoản người dùng mới. 
        Dữ liệu đầu vào được kiểm tra trước khi tạo tài khoản. 
        Mật khẩu sẽ được băm bằng Bcrypt trước khi lưu vào cơ sở dữ liệu."""),
)
def register(
    request: Request,
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    user = register_user(
        db,
        user_data.model_dump(),
    )

    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Đăng ký tài khoản thành công!",
        data=UserResponse.model_validate(user),
        path=request.url.path,
    )


# Đăng nhập
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập",
    description=("""Đăng nhập vào hệ thống bằng username và password. 
        Hệ thống xác thực thông tin đăng nhập bằng Bcrypt 
        và cấp phát Access Token JWT nếu thông tin hợp lệ."""),
)
def login(
    request: Request,
    login_data: UserLoginRequest,
    db: Session = Depends(get_db),
):
    token = login_user(
        db,
        login_data.model_dump(),
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Đăng nhập thành công!",
        data=TokenResponse.model_validate(token),
        path=request.url.path,
    )
