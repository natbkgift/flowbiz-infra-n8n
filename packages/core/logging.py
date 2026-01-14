import logging
import sys

from packages.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    log_level = getattr(logging, settings.app_log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
