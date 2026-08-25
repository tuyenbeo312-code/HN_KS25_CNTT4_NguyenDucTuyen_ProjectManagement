from fastapi import APIRouter, Depends, status, Request
from app.dependencies.auth import get_current_admin
from app.models.user import UserModel
from app.core.exceptions import create_response

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
def admin_dashboard(request: Request, admin: UserModel = Depends(get_current_admin)):
    """Chỉ Admin mới có quyền truy cập."""
    return create_response(
        status_code=status.HTTP_200_OK,
        message=f"Xin chào Admin {admin.full_name}!",
        data={"role": admin.role},
        path=request.url.path,
    )
