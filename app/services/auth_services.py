from jwt import PyJWTError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import UserModel


def get_user_by_email(db: Session, email: str):
    """Tìm kiếm user trong DB theo email."""
    return db.query(UserModel).filter(UserModel.email == email).first()


def register_user(db: Session, user_data: dict):
    """Đăng ký user mới: kiểm tra trùng email, băm mật khẩu và lưu vào DB."""
    if get_user_by_email(db, user_data["email"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email đã tồn tại"
        )
    hashed_pw = get_password_hash(user_data["password"])
    new_user = UserModel(
        full_name=user_data["full_name"],
        password_hash=hashed_pw,
        email=user_data["email"],
        role=user_data.get("role", "USER"),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(db: Session, login_data: dict) -> dict:
    """Xác thực đăng nhập và cấp token JWT."""
    user = get_user_by_email(db, login_data["email"])
    if not user or not verify_password(login_data["password"], user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản của bạn đã bị khóa",
        )
    access_token = create_access_token({"sub": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
