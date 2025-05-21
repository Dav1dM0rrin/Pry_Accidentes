# chatbot/bot_logging.py
import logging
import sys

def setup_logging():
    """Configura el logging para el bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)
    logger.info("Logging configurado.")
    return logger
