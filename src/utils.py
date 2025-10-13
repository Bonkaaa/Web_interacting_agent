import logging
import os 
from pathlib import Path

def setup_logger(name: str, level = logging.INFO):
    """
    Set up a logger that writes to a file in the logs directory.
    Args:
        name (str): The name of the logger.
        level: The logging level (default: logging.INFO).
    Returns:
        logging.Logger: Configured logger instance.
    """
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt = "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_dir / f"{name}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger