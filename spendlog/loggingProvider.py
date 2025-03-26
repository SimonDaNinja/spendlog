import logging
import os

# Minimalist singleton to access the logging module
#
# Its main purpose is that I don't want to have to think about where and when
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

# I also do some hacking to add another log level, which is probably not guaranteed
# to be stable in all versions of logging, since it is dependent on its internals rather
# than its API, and it is probably ill adviced in general.
#
# I may decide that's too imprudent one day. But that day is not today

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
        cls._instance.addLoglevelEverything()
        cls.logging = logging

    # NOTE! This function uses a lot of stuff that is "private" to logging, and isn't part
    # of its API.
    # thus it is *not* guaranteed to work
    @classmethod
    def addLoglevelEverything(cls):
        try:
            EVERYTHING = 1

            _is_internal_frame_original = logging._is_internal_frame

            def logger_everything(self, msg, *args, **kwargs):
                if self.isEnabledFor(EVERYTHING):
                    self._log(EVERYTHING, msg, args, **kwargs)

            def logging_everything(msg, *args, **kwargs):
                root = logging.Logger.root
                if len(root.handlers) == 0:
                    logging.basicConfig()
                root.everything(msg, *args, **kwargs)

            def _is_internal_frame_replacement(frame):
                thisfile=os.path.normcase(logger_everything.__code__.co_filename)
                filename = os.path.normcase(frame.f_code.co_filename)
                if thisfile == filename:
                    return True
                return _is_internal_frame_original(frame)

            logging.EVERYTHING = EVERYTHING
            logging._is_internal_frame = _is_internal_frame_replacement
            logging.addLevelName(logging.EVERYTHING, "EVERYTHING")
            logging.everything = logging_everything
            logging.Logger.everything = logger_everything
        except Exception as e:
            logging.warning(f'Failed to define logging level EVERYTHING with the following exception:\n\n"{e}"\n\nUsing DEBUG level for EVERYTHING level prints instead')
            logging.everything = logging.debug
            logging.EVERYTHING = logging.DEBUG

    @classmethod
    def reset(cls):
        cls._instance = None
