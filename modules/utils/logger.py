import logging
from .path_manager import makeRelPath

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

def makeLogger(name, log_file, level=logging.INFO):
    """
    Base setup for logger
    
    Args:
         name (str): The name of the logger
         file (str): The path to the log file
         level : Level of the logging

    Returns:
         loggger : Instance of logger class 
    """

    handler = logging.FileHandler(log_file, mode='w')        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

