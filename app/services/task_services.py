from fastapi import HTTPException, status as http_status
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.models.project_member import ProjectMember
from app.models.user import UserModel


def create_task(db: Session, project_id: int, task_data: TaskCreate, current_user):

    # kiểm tra project có tồn tại không
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Project không tồn tại"
        )
    # kiểm tra current user có phải member của project không
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
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của project",
        )
    if task_data.assignee_id is not None:
        assignee = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == task_data.assignee_id,
            )
            .first()
        )

        if not assignee:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Assignee phải là thành viên của project",
            )
    # tạo task
    task = Task(
        project_id=project_id,
        title=task_data.title,
        description=task_data.description,
        assignee_id=task_data.assignee_id,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_project_tasks(
    db: Session,
    project_id: int,
    current_user,
    status: str | None = None,
    priority: str | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    # kiểm tra project tồn tại
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project không tồn tại"
        )
    # kiểm tra user có thuộc project không
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
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập project này",
        )
    query = db.query(Task).filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    # sort
    if sort_by == "created_at":
        sort_column = Task.created_at
    elif sort_by == "due_date":
        sort_column = Task.due_date
    else:
        raise HTTPException(
            status_code=400,
            detail="sort_by chỉ được là created_at hoặc due_date",
        )

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # pagination
    tasks = query.offset(offset).limit(limit).all()

    return tasks


# tìm task theo id, chỉ thành viên mới đc xem
def get_task_by_id(db: Session, task_id: int, current_user):
    # kiểm tra task có tồn tại không
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Task không tồn tại!"
        )
    # kiểm tra current_user có thuộc project của task không
    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user.id,
        )
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của project này!",
        )

    return task


# cập nhật task, chỉ owner
def update_task(
    db: Session, task_id: int, task_data: TaskUpdate, current_user: UserModel
):
    # kiểm tra task tồn tại
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task không tồn tại")
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Project không tồn tại"
        )
    # kiểm tra current user có phải owner project không
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Chỉ OWNER mới được cập nhật task",
        )
    # chỉ lấy những trường được gửi lên
    data = task_data.model_dump(exclude_unset=True)
    # nếu như cập nhật assignee_id | assignee_id not None
    if "assignee_id" in data and data["assignee_id"] is not None:
        member = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == task.project_id,
                ProjectMember.user_id == data["assignee_id"],
            )
            .first()
        )
        if not member:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Assignee phải là thành viên của project",
            )
    # cập nhật những trường đó vào task
    for key, value in data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)

    return task


def delete_task(db: Session, task_id: int, current_user: UserModel):
    # kiểm tra task tồn tại
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Task không tồn tại"
        )
    # kiểm tra project tồn tại
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Project không tồn tại"
        )
    # chỉ OWNER của project mới được xóa task
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Chỉ OWNER mới có quyền xóa task",
        )
    deleted_task = {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "assignee_id": task.assignee_id,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date,
        "created_at": task.created_at,
    }
    db.delete(task)
    db.commit()

    return deleted_task
