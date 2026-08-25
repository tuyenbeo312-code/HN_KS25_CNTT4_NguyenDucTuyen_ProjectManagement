from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.database import Base


class Task(Base):
    __tablename__ = "tasks"
    # Mã task
    id = Column(Integer, primary_key=True, index=True)
    # Task thuộc dự án
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    # Tiêu đề
    title = Column(String(255), nullable=False)
    # Mô tả
    description = Column(Text, nullable=True)
    # Người được giao
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # trạng thái của dự án : TODO / IN_PROGRESS / DONE
    status = Column(Enum("TODO", "IN_PROGRESS", "DONE"), nullable=False)
    # độ ưu tiên của dự án : LOW / MEDIUM / HIGH
    priority = Column(Enum("LOW", "MEDIUM", "HIGH"), nullable=False)
    # Hạn xử lý
    due_date = Column(DateTime, nullable=True)
    # Ngày tạo
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # task thuộc Project
    project = relationship("Project", back_populates="tasks")

    # task được giao cho User
    assignee = relationship("UserModel", back_populates="tasks")
