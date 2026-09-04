import logging
from pathlib import Path
from logger_config import get_logger, setup_logging, get_log_file



def test_get_logger_instance():
    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "PersonalFinance.test_module"


def test_logger_file_output(temp_data_dir):
    setup_logging()
    logger = get_logger("file_test")
    test_msg = "Unique test log message for pytest verification"
    logger.info(test_msg)

    # Flush handlers to ensure content is written to disk
    for handler in logger.handlers:
        handler.flush()

    log_path = temp_data_dir / "data" / "app.log"
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert test_msg in content

