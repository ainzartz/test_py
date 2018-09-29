import logging
import os
import sys 
#import configparser

logger = logging.getLogger("main ") 
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

#config = configparser.ConfigParser()

def main():
    logger.debug("debug")
    logger.info("info")
    logger.error("error")
    logger.warning("warr")
    logger.critical("critical")


if __name__ == '__main__':

    # adjust path if this main class is packed executable.
    #if __package__ is None and not hasattr(sys, 'frozen'):
    #    sys.path.insert(0, os.path.dirname(os.path.dirname(
    #        os.path.realpath(os.path.abspath(__file__)))))

    sys.exit(main())
