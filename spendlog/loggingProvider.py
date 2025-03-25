import logging

class LoggingProvider:

    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._init()
        return cls._instance

    def _init(self):
        logFormat = "[%(asctime)s] %(funcName)s(), %(filename)s:%(lineno)d (%(levelname)s): \"%(message)s\""
        logging.basicConfig(
            level = logging.WARNING,
            format = logFormat,
            datefmt="%Y-%m-%d"
        )
        self.logging = logging
        self.logging.debug(f"LoggingProvider initialized")

    @classmethod
    def reset(cls):
        cls._instance = None
