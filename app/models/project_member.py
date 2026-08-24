from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.database import Base


class ProjectMember(Base):
    __tablename__ = "project_members"
    # Dự án
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    # Thành viên
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    # vai trò trong dự án : OWNER / MEMBER
    role = Column(Enum("OWNER", "MEMBER"), nullable=False, default="MEMBER")
    # Ngày tham gia
    joined_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="members")

    user = relationship("UserModel", back_populates="project_members")
