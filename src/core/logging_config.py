"""Logging configuration for the application."""
import logging
import sys
from logging.config import dictConfig

from core import config


def setup_logging():
    """Configure logging for the application."""
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": config.LOG_LEVEL,
                "formatter": "default",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "app": {
                "handlers": ["console"],
                "level": config.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": config.LOG_LEVEL,
        },
    }
    
    dictConfig(log_config)
    return logging.getLogger("app")


# Create logger instance
logger = setup_logging()
