from fastapi.exceptions import RequestValidationError
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime


def create_response(status_code=None, message=None, data=None, errors=None, path=None):
    return JSONResponse(
        status_code=status_code,
        content={
            "statusCode": status_code,
            "message": message,
            "data": jsonable_encoder(data),
            "errors": errors,
            "timestamp": datetime.now().isoformat(),
            "path": path,
        },
    )


def exception(app):

    @app.exception_handler(HTTPException)
    async def http_exception_handle(request: Request, exc: HTTPException):
        return create_response(
            status_code=exc.status_code, message=exc.detail, path=request.url.path
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handle(
        request: Request, exc: RequestValidationError
    ):
        return create_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Dữ liệu không hợp lệ!",
            errors=exc.errors(),
            path=request.url.path,
        )

    @app.exception_handler(Exception)
    async def exception_handle(request: Request, exc: Exception):
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Lỗi hệ thống!",
            path=request.url.path,
        )
