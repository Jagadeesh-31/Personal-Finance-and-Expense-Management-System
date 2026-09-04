import logging
from pathlib import Path


def get_log_file():
    """Get the log file path relative to current working directory."""
    log_dir = Path.cwd() / "data"
    log_dir.mkdir(exist_ok=True)
    return log_dir / "app.log"


def setup_logging(log_level=logging.INFO):
    """Configure root logger with console and file handlers."""
    logger = logging.getLogger("PersonalFinance")
    logger.setLevel(log_level)

    log_file = get_log_file()

    # Check if file handler for current log_file exists
    file_handler_exists = any(
        isinstance(h, logging.FileHandler)
        and Path(h.baseFilename).resolve() == log_file.resolve()
        for h in logger.handlers
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if not file_handler_exists:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    console_handler_exists = any(
        type(h) is logging.StreamHandler for h in logger.handlers
    )

    if not console_handler_exists:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name=None):
    """Get a logger instance for a specific module or component."""
    base_logger = setup_logging()
    if name:
        return base_logger.getChild(name)
    return base_logger

