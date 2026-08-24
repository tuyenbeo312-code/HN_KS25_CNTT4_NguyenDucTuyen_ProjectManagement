from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.sercurity import decode_access_token
from app.services.auth_services import get_user_by_email
from app.models.user import UserModel

# Khởi tạo Security Scheme để Swagger UI hiển thị nút 'Authorize'
security = HTTPBearer()


# 1. XÁC THỰC (Authentication) - Lấy thông tin user từ JWT Token
def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UserModel:
    token = cred.credentials  # Tự động trích xuất chuỗi token sau 'Bearer '
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
        )
    user = get_user_by_email(db, payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Không tìm thấy người dùng"
        )
    return user


def get_current_admin(current_user: UserModel = Depends(get_current_user)):
    """Chỉ cho phép tài khoản Admin truy cập."""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Admin mới có quyền truy cập",
        )

    return current_user
