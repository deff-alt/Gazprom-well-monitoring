"""Единый формат ошибок API по RFC 7807."""
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def install_problem_handlers(app, logger):
    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse(
            status_code=422,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": "Ошибка валидации",
                "status": 422,
                "detail": "Проверьте переданные поля запроса",
                "instance": request.url.path,
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, exc):
        detail = exc.detail if isinstance(exc.detail, str) else "Запрос не может быть выполнен"
        titles = {400: "Некорректный запрос", 401: "Требуется авторизация", 403: "Доступ запрещён", 404: "Ресурс не найден", 409: "Конфликт запроса", 422: "Ошибка обработки запроса", 502: "Ошибка зависимого сервиса", 503: "Сервис временно недоступен"}
        return JSONResponse(
            status_code=exc.status_code,
            media_type="application/problem+json",
            headers=exc.headers,
            content={
                "type": "about:blank",
                "title": titles.get(exc.status_code, "Ошибка запроса"),
                "status": exc.status_code,
                "detail": detail,
                "instance": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def internal_error(request, exc):
        logger.exception("Необработанная ошибка при обработке %s", request.url.path)
        return JSONResponse(
            status_code=500,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": "Внутренняя ошибка сервера",
                "status": 500,
                "detail": "Внутренняя ошибка сервиса",
                "instance": request.url.path,
            },
        )
