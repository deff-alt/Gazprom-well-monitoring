import logging
import time

from fastapi import FastAPI, Request


def install_request_logging(app: FastAPI, logger: logging.Logger) -> None:
    """Логирует HTTP-запросы, ответы и необработанные исключения без тел запросов."""

    @app.middleware("http")
    async def log_http_requests(request: Request, call_next):
        started_at = time.perf_counter()
        client_host = request.client.host if request.client else "unknown"

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.exception(
                "HTTP request failed method=%s path=%s client=%s duration_ms=%.2f",
                request.method,
                request.url.path,
                client_host,
                elapsed_ms,
            )
            raise

        elapsed_ms = (time.perf_counter() - started_at) * 1000
        log_method = logger.warning if response.status_code >= 400 else logger.info
        log_method(
            "HTTP request method=%s path=%s status=%s client=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            client_host,
            elapsed_ms,
        )
        return response
