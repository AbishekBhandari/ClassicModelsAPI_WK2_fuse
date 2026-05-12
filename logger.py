import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "app.log")
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

if not logging.getLogger().handlers:
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


# Backward compatibility for modules importing `logger` directly.
logger = get_logger("app")