# utils.py
import logging
from typing import Optional


def setup_logger(name, log_file: Optional[str], level=logging.INFO) -> logging.Logger:
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if log_file:
        logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    return logger
