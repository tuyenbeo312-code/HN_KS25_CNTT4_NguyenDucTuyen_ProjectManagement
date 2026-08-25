from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import Base, engine, get_db
from app.routers.user_routers import router as user_router
from app.routers.admin_routers import router as admin_router
from app.routers.auth_routers import router as auth_router
from app.routers.project_router import router as project_router
from app.routers.task_routers import router as task_router
from app.core.exceptions import exception
from app import models

app = FastAPI()

exception(app)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(project_router)
app.include_router(task_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"message": "Kết nối database thành công", "result": result}
