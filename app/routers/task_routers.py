from fastapi import APIRouter, Depends, status, Request, Query
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.models.user import UserModel
from app.core.exceptions import create_response

from app.services.task_services import (
    create_task,
    get_project_tasks,
    get_task_by_id,
    update_task,
    delete_task,
)

router = APIRouter(tags=["Tasks"])


# Tạo task
@router.post(
    "/projects/{project_id}/tasks",
    status_code=status.HTTP_201_CREATED,
    summary="Tạo task mới",
    description=("""Tạo một task mới thuộc project.
        Người dùng phải là thành viên của project và có quyền tạo task.
        Thông tin task gồm title, description, assignee, status, 
        priority và due_date."""),
)
def create_project_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return create_task(
        db=db,
        project_id=project_id,
        task_data=task_data,
        current_user=current_user,
    )


# Lấy danh sách task theo project
@router.get(
    "/projects/{project_id}/tasks",
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách task",
    description=("""Lấy danh sách các task thuộc project mà người dùng hiện tại 
        có quyền truy cập. 
        Hỗ trợ lọc theo status, priority và assignee;
        tìm kiếm theo title; phân trang và sắp xếp kết quả."""),
)
def get_tasks(
    project_id: int,
    request: Request,
    task_status: str | None = Query(
        None,
        alias="status",
        description="Lọc task theo trạng thái.",
    ),
    priority: str | None = Query(
        None,
        description="Lọc task theo độ ưu tiên.",
    ),
    assignee_id: int | None = Query(
        None,
        description="Lọc task theo ID người được giao.",
    ),
    search: str | None = Query(
        None,
        description="Tìm kiếm task theo tiêu đề.",
    ),
    limit: int = Query(
        10,
        ge=1,
        description="Số lượng task tối đa được trả về.",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Số lượng task bỏ qua trước khi lấy dữ liệu.",
    ),
    sort_by: str = Query(
        "due_date",
        description="Trường dùng để sắp xếp task.",
    ),
    sort_order: str = Query(
        "desc",
        description="Thứ tự sắp xếp: asc hoặc desc.",
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    tasks = get_project_tasks(
        db=db,
        project_id=project_id,
        current_user=current_user,
        status=task_status,
        priority=priority,
        assignee_id=assignee_id,
        search=search,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách task thành công!",
        data=tasks,
        path=request.url.path,
    )


# Lấy task theo ID
@router.get(
    "/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết task",
    description=("""Lấy thông tin chi tiết của một task. 
        Người dùng phải có quyền truy cập vào project chứa task."""),
)
def get_task(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = get_task_by_id(
        db=db,
        task_id=task_id,
        current_user=current_user,
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy task thành công!",
        data=task,
        path=request.url.path,
    )


# Cập nhật task
@router.patch(
    "/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Cập nhật task",
    description=("""Cập nhật một hoặc nhiều trường của task.
        Các trường không được gửi lên sẽ giữ nguyên giá trị hiện tại."""),
)
def update_task_api(
    task_id: int,
    task_data: TaskUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = update_task(
        db,
        task_id,
        task_data,
        current_user,
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Cập nhật task thành công!",
        data=task,
        path=request.url.path,
    )


# Xóa task
@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa task",
    description=("""Xóa một task khỏi project. 
        Người dùng phải có quyền thực hiện thao tác xóa task."""),
)
def delete_task_api(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    deleted_task = delete_task(
        db=db,
        task_id=task_id,
        current_user_id=current_user.id,
    )

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Xóa task thành công!",
        data=deleted_task,
        path=request.url.path,
    )
