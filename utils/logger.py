import logging
import sys

def setup_logger(name, level=logging.INFO):
    """
    Set up and return a logger with the given name and level.
    
    Args:
        name: The name of the logger
        level: The logging level (default: INFO)
    
    Returns:
        logging.Logger: Configured logger
    """
    # Configure logging format
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    return logger

# Global application logger
app_logger = setup_logger("DAR") 