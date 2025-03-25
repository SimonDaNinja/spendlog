import logging
from datetime import datetime

class Logger:

    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._init()
        return cls._instance

    def _init(self):
        logFormat = "[%(asctime)s] %(funcName)s(), %(filename)s:%(lineno)d (%(levelname)s): \"%(message)s\""
        logging.basicConfig(
            level = logging.DEBUG,
            format = logFormat,
            datefmt="%Y-%m-%d"
        )
        self.logging = logging