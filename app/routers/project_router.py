from fastapi import APIRouter, Depends, status, Request, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import UserModel
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from app.schemas.project_member_schema import ProjectMemberCreate
from app.services.project_services import (
    create_project,
    get_projects,
    get_project_by_id,
    update_project,
    delete_project,
    add_member_to_project,
    remove_project_member,
    get_project_members_service,
)
from app.core.exceptions import create_response

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


# Tạo dự án
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Tạo dự án mới",
    description=("""Tạo một dự án mới cho người dùng hiện tại. 
        Người tạo dự án sẽ tự động trở thành Owner của dự án."""),
)
def create(
    request: Request,
    project_data: ProjectCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = create_project(
        db=db,
        project_data=project_data,
        current_user=current_user,
    )

    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Tạo dự án thành công",
        data=project,
        path=request.url.path,
    )


# Lấy danh sách dự án
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách dự án",
    description=("""Lấy danh sách các dự án mà người dùng hiện tại là 
        Owner hoặc Member. Có thể tìm kiếm theo tên dự án."""),
)
def get_project_list(
    request: Request,
    search: str | None = Query(default=None, description="Tìm kiếm dự án theo tên"),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    projects = get_projects(
        db=db,
        current_user=current_user,
        search=search,
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách dự án thành công",
        data=projects,
        path=request.url.path,
    )


# Lấy dự án theo ID
@router.get(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết dự án",
    description=("""Lấy thông tin chi tiết của một dự án. 
        Chỉ thành viên của dự án mới có quyền xem thông tin."""),
)
def get_project(
    project_id: int,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = get_project_by_id(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy thông tin dự án thành công",
        data=project,
        path=request.url.path,
    )


# Cập nhật dự án
@router.put(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    summary="Cập nhật dự án",
    description=("""Cập nhật thông tin của một dự án. 
        Chỉ Owner của dự án mới có quyền thực hiện thao tác này."""),
)
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


# Xóa dự án
@router.delete(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa dự án",
    description=(
        """Xóa một dự án khỏi hệ thống. Chỉ Owner của dự án mới có quyền xóa dự án."""
    ),
)
def delete(
    request: Request,
    project_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted_project = delete_project(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Xóa dự án thành công",
        data=deleted_project,
        path=request.url.path,
    )


# Thêm member vào dự án
@router.post(
    "/{project_id}/members",
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên vào dự án",
    description=("""Thêm một người dùng vào dự án. 
        Chỉ Owner mới có quyền thêm thành viên. 
        Không được thêm người dùng đã là thành viên của dự án."""),
)
def add_member(
    project_id: int,
    data: ProjectMemberCreate,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member = add_member_to_project(
        db=db,
        project_id=project_id,
        current_user=current_user,
        data=data,
    )

    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Thêm thành viên vào dự án thành công",
        data=member,
        path=request.url.path,
    )


# Xóa member khỏi dự án
@router.delete(
    "/{project_id}/members/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa thành viên khỏi dự án",
    description=("""Xóa một thành viên khỏi dự án. 
        Chỉ Owner mới có quyền xóa thành viên. 
        Không được xóa Owner cuối cùng của dự án."""),
)
def delete_project_member(
    project_id: int,
    user_id: int,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted_member_data = remove_project_member(
        db=db,
        project_id=project_id,
        user_id=user_id,
        current_user=current_user,
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Xóa thành viên thành công!",
        data=deleted_member_data,
        path=request.url.path,
    )


# Lấy danh sách member
@router.get(
    "/{project_id}/members",
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách thành viên",
    description=("""Lấy danh sách tất cả thành viên của một dự án, 
        bao gồm thông tin user và vai trò của từng thành viên. 
        Người dùng phải có quyền truy cập vào dự án."""),
)
def get_project_members(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    members = get_project_members_service(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách thành viên thành công!",
        data=members,
        path=request.url.path,
    )
