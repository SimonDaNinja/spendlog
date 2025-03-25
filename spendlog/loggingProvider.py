import logging

# Minimalist singleton to access the logging module
#
# Its only purpose is that I don't want to have to think about where and when
# I run logging.basicConfig().
#
# By always getting the logging module through it, I can be sure that
# logging.basicConfig() has been run with the defaults I want exactly once
#
# I tend to use it in the import section of files as a replacement for importing
# logging directly.
#
# I.e, simply replacing this:
#
#       import logging
#
# with this
#
#       from spendlog.loggingProvider import LoggingProvider
#       logging = LoggingProvider().logging
#
# and then using logging as normal

class LoggingProvider:

    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._init()
        return cls._instance

    @classmethod
    def _init(cls):
        logFormat = "[%(asctime)s] %(funcName)s(), %(filename)s:%(lineno)d (%(levelname)s): \"%(message)s\""
        logging.basicConfig(
            level = logging.WARNING,
            format = logFormat,
            datefmt="%Y-%m-%d"
        )
        cls.logging = logging
        cls.logging.debug(f"LoggingProvider initialized")

    @classmethod
    def reset(cls):
        cls._instance = None
