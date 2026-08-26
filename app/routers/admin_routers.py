from fastapi import APIRouter, Depends, Request, status
from app.dependencies.auth import get_current_admin
from app.models.user import UserModel
from app.core.exceptions import create_response

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    summary="Truy cập trang quản trị",
    description=("""Kiểm tra quyền truy cập của tài khoản Admin. 
        Chỉ người dùng có role ADMIN mới được phép truy cập endpoint này. 
        Endpoint trả về thông tin cơ bản của Admin hiện tại."""),
)
def admin_dashboard(
    request: Request,
    admin: UserModel = Depends(get_current_admin),
):
    return create_response(
        status_code=status.HTTP_200_OK,
        message=f"Xin chào Admin {admin.full_name}!",
        data={
            "role": admin.role,
        },
        path=request.url.path,
    )
