import logging
from pathlib import Path

from rich.logging import RichHandler

import config


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a module. Call this at the top of every file:

        from utils.logger import get_logger
        log = get_logger(__name__)

    Then use:
        log.info("Server started")
        log.warning("Upstream timeout")
        log.error("Failed to load blocklist")
        log.debug("Query received: example.com")
    """
    logger = logging.getLogger(name)

    # Don't add handlers twice if get_logger is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

    # ── Console handler (Rich — pretty colours in terminal) ──────────────────
    console = RichHandler(
        rich_tracebacks=True,
        show_path=False,        # don't print full file path on every line
        markup=True,
    )
    console.setLevel(logging.DEBUG)
    logger.addHandler(console)

    # ── File handler (plain text, always DEBUG level for full history) ────────
    file_handler = logging.FileHandler(config.LOG_PATH, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(file_handler)

    return logger
