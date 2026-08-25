from fastapi import APIRouter, Depends, status, Request, Query
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
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


# tạo task
@router.post(
    "/projects/{id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_task(
    id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_task(
        db=db, project_id=id, task_data=task_data, current_user=current_user
    )


# lấy ra danh sách task theo id của project
@router.get("/projects/{project_id}/tasks")
def get_tasks(
    project_id: int,
    request: Request,
    task_status: str | None = Query(None, alias="status"),
    priority: str | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    sort_by: str = "due_date",
    sort_order: str = "desc",
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


# lấy ra task theo id
@router.get("/tasks/{id}")
def get_task(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = get_task_by_id(db=db, task_id=id, current_user=current_user)

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy task thành công!",
        data=task,
        path=request.url.path,
    )


@router.patch("/tasks/{id}")
def update_task_api(
    id: int,
    task_data: TaskUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = update_task(db, id, task_data, current_user)

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Cập nhật task thành công",
        data=task,
        path=request.url.path,
    )


@router.delete("/task/{id}")
def delete_task_api(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    deleted_task = delete_task(db=db, task_id=id, current_user_id=current_user.id)

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Xóa task thành công",
        data=deleted_task,
        path=request.url.path,
    )
