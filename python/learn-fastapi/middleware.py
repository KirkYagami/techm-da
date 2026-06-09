"""
In FastAPI, middleware is a function or class that runs with every request before it is processed by a path operation, and again with the response before it is returned.

This allows developers to implement logic for cross-cutting concerns like logging, authentication, and performance monitoring in a single place. 

"""

from fastapi import Request
import logging
import time
import os


logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

log_path = os.path.abspath("app.log")


if not logger.handlers:
    file_handler = logging.FileHandler(log_path, mode="a",)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    print("Logging to:", log_path)


async def log_requests(request: Request, call_next):
    """log every request with method, path, status code and duration"""

    start_time = time.time()

    logger.info(f"-> {request.method} {request.url.path} | {request.client.host}")
    response = await call_next(request)

    duration = (time.time() - start_time) *1000 # in MS

    logger.info(
        f"<- {request.method} {request.url.path} "
        f"| {response.status_code} "
        f"| {duration:.2f}ms"
    )

    return response











