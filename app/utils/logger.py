from pathlib import Path
from loguru import logger
import sys

# Create logs folder automatically
Path("logs").mkdir(exist_ok=True)

logger.remove()

# Console Log
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
)

# File Log
logger.add(
    "logs/app.log",
    rotation="1 MB",
    retention="10 days",
    compression="zip",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
)