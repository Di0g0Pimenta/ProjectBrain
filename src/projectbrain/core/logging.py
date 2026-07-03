from loguru import logger

logger.remove()

logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO",
)

app_logger = logger