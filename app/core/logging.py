import logging
import sys

from app.core.config import get_settings

settings = get_settings()

def setup_logging() -> None:
    root_logger = logging.getLogger()

    if root_logger.hasHandlers():
        return # already configured (reload/tests)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOGGING_LEVEL.upper())


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)