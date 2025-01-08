import time
import logging

from lib.logging_config import logger


logger = logging.getLogger(__name__)

def measure_time(func):
    def wrapper( *args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.debug(f"Function '{func.__name__}' executed in {elapsed_time:.4f}s.\n")
        return result
    
    return wrapper
