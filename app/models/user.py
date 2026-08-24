from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.database import Base


class UserModel(Base):
    __tablename__ = "users"
    # mã người dùng
    id = Column(Integer, primary_key=True, index=True)
    # email đăng nhập
    email = Column(String(255), unique=True, nullable=False)
    # mật khẩu đã hash
    password_hash = Column(String(255), nullable=False)
    # Họ tên
    full_name = Column(String(255), nullable=False)
    # Vai trò : USER / ADMIN
    role = Column(Enum("USER", "ADMIN"), nullable=False)
    # Trạng thái tài khoản
    is_active = Column(Boolean, default=True, nullable=False)
    # Ngày tạo
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    # user có nhiều project
    projects = relationship("Project", back_populates="owner")
    # user tham gia nhiều project
    project_members = relationship("ProjectMember", back_populates="user")
    # user có thể được giao nhiều task
    tasks = relationship("Task", back_populates="assignee")



