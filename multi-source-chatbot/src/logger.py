import logging
import logging.handlers
from config import settings
from pathlib import Path


def setup_logging():
    Path(settings.LOG_DIR).mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("chatbot")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    if logger.hasHandlers():
        return logger
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    file_handler = logging.handlers.RotatingFileHandler(
        Path(settings.LOG_DIR) / "chatbot.log",
        maxBytes=10485760,
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    query_handler = logging.FileHandler(
        Path(settings.LOG_DIR) / "queries.log"
    )
    query_handler.setFormatter(formatter)
    query_logger = logging.getLogger("queries")
    query_logger.addHandler(query_handler)
    
    return logger


logger = setup_logging()
query_logger = logging.getLogger("queries")
