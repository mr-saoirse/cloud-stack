from .schema import OrderStatus
from loguru import logger

def handler(message: OrderStatus):
    logger.info(f"handling message {message}")