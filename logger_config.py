import logging
from pathlib import Path

# Step 1: Define function to dynamically locate the log file path.
def get_log_file():
    """Get the log file path relative to current working directory."""
    # Step 1.1: Ensure data folder exists in current working directory
    log_dir = Path.cwd() / "data"
    log_dir.mkdir(exist_ok=True)
    # Step 1.2: Return absolute path to app.log
    return log_dir / "app.log"


# Step 2: Configure logging system with file and console handlers.
def setup_logging(log_level=logging.INFO):
    """Configure root logger with console and file handlers."""
    # Step 2.1: Instantiate base logger for PersonalFinance application
    logger = logging.getLogger("PersonalFinance")
    logger.setLevel(log_level)

    # Step 2.2: Retrieve log file path
    log_file = get_log_file()

    # Step 2.3: Check if file handler already attached to avoid duplicate log entries
    file_handler_exists = any(
        isinstance(h, logging.FileHandler)
        and Path(h.baseFilename).resolve() == log_file.resolve()
        for h in logger.handlers
    )

    # Step 2.4: Define standardized log output format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Step 2.5: Attach FileHandler if not already configured
    if not file_handler_exists:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Step 2.6: Check if console StreamHandler already attached
    console_handler_exists = any(
        type(h) is logging.StreamHandler for h in logger.handlers
    )

    # Step 2.7: Attach StreamHandler if not already configured
    if not console_handler_exists:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Step 2.8: Return configured logger instance
    return logger


# Step 3: Helper function to retrieve namespaced logger instances.
def get_logger(name=None):
    """Get a logger instance for a specific module or component."""
    # Step 3.1: Initialize base logger
    base_logger = setup_logging()
    # Step 3.2: Return child logger with component name if provided
    if name:
        return base_logger.getChild(name)
    return base_logger
