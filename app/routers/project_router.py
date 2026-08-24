from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import UserModel
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from app.schemas.project_member_schema import ProjectMemberCreate, ProjectMemberResponse
from app.services.project_services import (
    create_project,
    get_projects,
    get_project_by_id,
    update_project,
    delete_project,
    add_member_to_project,
    remove_project_member,
    get_project_members,
)
from app.core.exceptions import create_response

router = APIRouter(prefix="/projects", tags=["Projects"])


# tạo dự án
@router.post("/", status_code=status.HTTP_201_CREATED)
def create(
    request: Request,
    project_data: ProjectCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = create_project(
        db=db, project_data=project_data, current_user=current_user
    )

    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Tạo dự án thành công",
        data=project,
        path=request.url.path,
    )


# lấy ra danh sách dự án
@router.get("/")
def get_project_list(
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    projects = get_projects(db=db, current_user=current_user)

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách dự án thành công",
        data=projects,
        path=request.url.path,
    )


# lấy dự án theo id
@router.get("/{project_id}")
def get_project(
    project_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
):
    project = get_project_by_id(db=db, project_id=project_id, current_user=current_user)

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy thông tin dự án thành công",
        data=project,
        path=request.url.path,
    )


# cập nhật
@router.put("/{project_id}")
def update(
    request: Request,
    project_id: int,
    project_data: ProjectUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = update_project(
        db=db,
        project_id=project_id,
        project_data=project_data,
        current_user=current_user,
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Cập nhật dự án thành công",
        data=project,
        path=request.url.path,
    )


# xóa dự án
@router.delete("/{project_id}")
def delete(
    request: Request,
    project_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted_project = delete_project(
        db=db, project_id=project_id, current_user=current_user
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Xóa dự án thành công",
        data=deleted_project,
        path=request.url.path,
    )


@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: int,
    data: ProjectMemberCreate,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member = add_member_to_project(
        db=db, project_id=project_id, current_user=current_user, data=data
    )

    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Thêm thành viên vào dự án thành công",
        data=member,
        path=request.url.path,
    )


@router.delete("/{project_id}/members/{user_id}")
def delete_project_member(
    project_id: int,
    user_id: int,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted_member_data = remove_project_member(
        db=db, project_id=project_id, user_id=user_id, current_user=current_user
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Xóa thành viên thành công!",
        data=deleted_member_data,
        path=request.url.path,
    )


@router.get(
    "/{id}/members",
    response_model=list[ProjectMemberResponse],
    status_code=status.HTTP_200_OK,
)
def get_project_members_api(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return get_project_members(db, id)
