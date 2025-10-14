import logging
import os 
from pathlib import Path
import json

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

def dump_json_to_file(data: dict, filename: str):
    """
    Dump a dictionary to a JSON file.
    Args:
        data (dict): The data to dump.
        filename (str): The name of the file to write to.
    """
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_path = log_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def write_text_to_file(text: str, filename: str):
    """
    Write text to a file.
    Args:
        text (str): The text to write.
        filename (str): The name of the file to write to.
    """
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_path = log_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)