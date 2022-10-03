import logging
import os
import sys


def log_file():
    home = os.path.expanduser('~')
    logs_dir = os.path.join(home, 'EnviaBoleto')
    logs_path = os.path.join(logs_dir, 'log.txt')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    return logs_path


LOGGER = logging.getLogger(__name__)
STDOUT_HANDLER = logging.StreamHandler(stream=sys.stdout)
STDOUT_HANDLER.setLevel(logging.DEBUG)
FILE_HANDLER = logging.FileHandler(log_file())
FILE_HANDLER.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d - %(message)s', '%d/%m/%Y %H:%M:%S'))
FILE_HANDLER.setLevel(logging.DEBUG)
LOGGER.addHandler(STDOUT_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(logging.INFO)
