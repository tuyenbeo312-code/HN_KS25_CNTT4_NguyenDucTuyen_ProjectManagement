from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ProjectMemberBase(BaseModel):
    project_id: int
    user_id: int
    role: str


class ProjectMemberCreate(BaseModel):
    user_id: int


class ProjectMemberUpdate(BaseModel):
    role: str


class ProjectMemberResponse(ProjectMemberBase):
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
