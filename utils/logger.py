import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import colorlog


class Logger:
    dir = os.getcwd()
    logger = logging.getLogger("xmigrate")
    logger.setLevel(logging.DEBUG)

    colored_fmt = colorlog.ColoredFormatter("%(log_color)s%(levelname)-9s%(reset)s %(white)-s%(asctime)s%(reset)s [%(blue)s%(name)s%(reset)s] %(log_color)s%(message)s%(reset)s")
    stdoutHandler = colorlog.StreamHandler(stream=sys.stdout)
    stdoutHandler.setLevel(logging.DEBUG)
    stdoutHandler.setFormatter(colored_fmt)

    fmt = logging.Formatter("[%(name)s] %(asctime)s [%(levelname)s] %(message)s")
    fileHandler = RotatingFileHandler(f"{dir}/app.log", mode='a', maxBytes=10*1024*1024, backupCount=2)
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(fmt)

    logger.addHandler(stdoutHandler)
    logger.addHandler(fileHandler)
    

    @classmethod
    def debug(cls, message) -> None:
        cls.logger.debug(message)

    @classmethod
    def warning(cls, message) -> None:
        cls.logger.warning(message)

    @classmethod
    def info(cls, message) -> None:
        cls.logger.info(message)

    @classmethod
    def error(cls, message) -> None:
        cls.logger.error(message)

    @classmethod
    def critical(cls, message) -> None:
        cls.logger.critical(message)