# Logging Setup
# -------------
# Configures logging to file with rotation.

import logging
from logging.handlers import RotatingFileHandler

LOG_FILE = "scraper.log"

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())  # optional: log to console too
