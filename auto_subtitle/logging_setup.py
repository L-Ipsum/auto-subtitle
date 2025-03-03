import logging
from datetime import datetime
from pathlib import Path


# Create a function to set up handlers
def setup_logger() -> logging.Logger:
    LOG_LEVEL = logging.DEBUG
    log_path = Path(f"logs/{datetime.now().strftime('%Y-%m-%d')}.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler
    file_handler_format = "%(asctime)s :: %(levelname)s :: %(funcName)s - %(message)s"
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(file_handler_format))

    # Console handler
    console_handler_format = "%(levelname)s - %(message)s"
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(console_handler_format))

    # Attach handlers to the root logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
