from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import UserModel
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from app.schemas.project_member_schema import ProjectMemberCreate


# tạo dự án và cho current_user là owner
def create_project(db: Session, project_data: ProjectCreate, current_user: UserModel):
    project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id,
    )
    try:
        db.add(project)
        db.flush()
        member = ProjectMember(
            project_id=project.id, user_id=current_user.id, role="OWNER"
        )
        db.add(member)
        db.commit()
        db.refresh(project)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tạo dự án do dữ liệu không hợp lệ",
        )

    return project


# lấy ra tất cả dự án của current_user
def get_projects(
    db: Session,
    current_user: UserModel,
    search: str | None = None,
):
    query = (
        db.query(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .filter(ProjectMember.user_id == current_user.id)
    )
    if search:
        query = query.filter(Project.name.ilike(f"%{search}%"))

    return query.all()


# lấy ra dự án theo id, nếu như current_user là member/owner
def get_project_by_id(db: Session, project_id: int, current_user: UserModel):
    # Tìm project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dự án"
        )
    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem dự án này",
        )

    return project


# cập nhật dự án, chỉ owner của dự án mới có quyền
def update_project(
    db: Session, project_id: int, project_data: ProjectUpdate, current_user: UserModel
):
    # Tìm project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dự án"
        )
    # Kiểm tra OWNER
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ OWNER của dự án mới có quyền sửa dự án",
        )
    # Cập nhật dữ liệu
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    try:
        db.commit()
        db.refresh(project)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu cập nhật không hợp lệ",
        )

    return project


# xóa dự án, chỉ owner của dự án mới có quyền
def delete_project(db: Session, project_id: int, current_user: UserModel):
    # Tìm project
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dự án"
        )

    # Kiểm tra OWNER
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ OWNER mới có quyền xóa dự án",
        )
    deleted_project_data = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "owner_id": project.owner_id,
    }
    db.delete(project)
    db.commit()

    return deleted_project_data


# thêm member vào dự án
def add_member_to_project(
    db: Session, project_id: int, current_user: UserModel, data: ProjectMemberCreate
):
    # kiểm tra project có tồn tại không
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dự án"
        )
    # kiểm tra current_user có phải OWNER không
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ owner của dự án mới có thể thêm thành viên",
        )
    # kiểm tra user muốn thêm có tồn tại không
    user = db.query(UserModel).filter(UserModel.id == data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="không tìm thấy user"
        )
    # kiểm tra user đã là member của dự án hay chưa
    existing_member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == data.user_id,
        )
        .first()
    )
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User đã là thành viên của dự án này",
        )
    # tạo member
    new_member = ProjectMember(
        project_id=project_id, user_id=data.user_id, role="MEMBER"
    )
    try:
        db.add(new_member)
        db.commit()
        db.refresh(new_member)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User đã là thành viên của dự án này",
        )
    return new_member


# xóa member khỏi project
def remove_project_member(
    db: Session, project_id: int, user_id: int, current_user: UserModel
):
    # kiểm tra project tồn tại
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="không tìm thấy dự án"
        )
    # kiểm tra current user có phải OWNER không
    current_member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
        .first()
    )
    if not current_member or current_member.role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ owner của dự án mới có thể xóa thành viên",
        )
    # kiểm tra user cần xóa có tồn tại không
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="không tìm thấy user"
        )
    # kiểm tra user có phải member của project không
    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user ko phải thành viên của dự án",
        )
    # không được xóa OWNER cuối cùng
    if member.role == "OWNER":
        owner_count = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id, ProjectMember.role == "OWNER"
            )
            .count()
        )
        if owner_count == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ko thể xóa owner cuối cùng",
            )
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OWNER không thể tự xóa mình khỏi dự án",
        )
    deleted_member_data = {
        "project_id": member.project_id,
        "user_id": member.user_id,
        "role": member.role,
    }
    db.delete(member)
    db.commit()
    return deleted_member_data


# lấy ra danh sách member và role trong dự án
def get_project_members_service(db: Session, project_id: int, current_user: UserModel):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project không tồn tại"
        )
    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem thành viên của dự án này",
        )
    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
