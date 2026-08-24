from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"
    # Mã dự án
    id = Column(Integer, primary_key=True, index=True)
    # Tên dự án
    name = Column(String(255), nullable=False)
    # Mô tả
    description = Column(Text, nullable=True)
    # Người sở hữu
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Ngày tạo
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    # project thuộc về một User
    owner = relationship("UserModel", back_populates="projects")
    # project có nhiều member
    members = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )
    # project có nhiều task
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
