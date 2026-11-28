import logging
import os


def configure_logging(default_name: str) -> logging.Logger:
    """Настраивает единый формат логирования для микросервиса."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
    return logging.getLogger(os.getenv("SERVICE_NAME", default_name))
