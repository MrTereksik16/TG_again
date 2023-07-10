import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s (Line: %(lineno)d) [%(filename)s]')
logger = logging.getLogger(__name__)

if not os.path.isdir("logs"):
    os.mkdir("logs")

handler = logging.FileHandler('logs/warning.log')

handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s (Line: %(lineno)d) [%(filename)s]')

handler.setFormatter(formatter)

logger.addHandler(handler)
