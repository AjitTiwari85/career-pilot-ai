from loguru import logger
import sys


logger.remove()


logger.add(
    sys.stdout,
    level="INFO",
    format="{time:HH:mm:ss} | {level} | {message}",
)

logger.add(
    "logs/app.log",
    rotation="1 MB",
    level= "INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)