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
        EverythingTraceLogLevelAdder()
        cls.logging = logging

    @classmethod
    def reset(cls):
        cls._instance = None

EVERYTHING = 1

class ModuleModder:

    def __init__(self, modifications):
        self.modifications = modifications
        self.executeAllModifications()

    def executeAllModifications(self):
        for modification in self.modifications:

            modification.wrapInjectionsInErrorHandling(self.wrapFunctionInErrorHandling)

            doBeforeModify = self.wrapFunctionInErrorHandling(modification.doBeforeModify)
            doBeforeModify()

            self.addRestoreStepToHandling(modification.restore)
            modify = self.wrapFunctionInErrorHandling(modification.modify)

            if not modify():
                return

    def wrapFunctionInErrorHandling(self, func):
        def wrapped(*args, **kwargs):
            try:
                func(*args, **kwargs)
                return True
            except Exception as e:
                self.handleError(e)
                return False
        return wrapped

    def handleError(self, e):
        print(f"Failed to modify module with the following error: {e}")

    # In theory, making a modification that causes an error means we should proceed to restore
    # the module modifications in the reverse order from what we made them (this way we are sure
    # that we take the same path back as we took on the way in)
    def addRestoreStepToHandling(self, restore):
        oldHandleError = self.handleError
        def newHandleError(e):
            restore()
            oldHandleError(e)
        self.handleError = newHandleError

class EverythingTraceLogLevelAdder(ModuleModder):
    def __init__(self):
        super().__init__(
            [
                FirstEverythingAdderModification(),
                ReplaceIsInternalFrameModification(),
                AddLevelEverythingModification(),
                AddLoggerEverythingModification(),
                AddLoggingEverythingModification()
            ]
        )

    def handleError(self, e):
        logging.error(f'Failed to define logging level EVERYTHING with the following exception:\n\n"{e}"\n\nUsing DEBUG level for EVERYTHING level prints instead')


class ModuleModification:
    def doBeforeModify(self):
        pass

    def modify(self):
        pass

    def restore(self):
        pass

    def wrapInjectionsInErrorHandling(self, wrap):
        pass

class FirstEverythingAdderModification(ModuleModification):

    def restore(self):
        logging.Logger.everything = logging.Logger.debug
        logging.EVERYTHING = logging.DEBUG
        logging.everything = logging.debug


class ReplaceIsInternalFrameModification(ModuleModification):

    def doBeforeModify(self):
        self._is_internal_frame_original = logging._is_internal_frame

    def restore(self):
        logging.is_internal_frame = self._is_internal_frame_original

    def modify(self):
        logging._is_internal_frame = self._is_internal_frame_replacement

    def _is_internal_frame_replacement(self, frame):
        thisfile=os.path.normcase(self.restore.__code__.co_filename)
        filename = os.path.normcase(frame.f_code.co_filename)
        if thisfile == filename:
            return True
        return self._is_internal_frame_original(frame)

    def wrapInjectionsInErrorHandling(self, wrap):
        self._is_internal_frame_replacement = wrap(self._is_internal_frame_replacement)

class AddLevelEverythingModification(ModuleModification):

    def modify(self):
        logging.EVERYTHING = EVERYTHING
        logging.addLevelName(logging.EVERYTHING, "EVERYTHING")

class AddLoggerEverythingModification(ModuleModification):

    def modify(self):
        logging.Logger.everything = self.logger_everything

    def logger_everything(self, loggerSideSelf, msg, *args, **kwargs):
        if loggerSideSelf.isEnabledFor(EVERYTHING):
            loggerSideSelf._log(EVERYTHING, msg, args, **kwargs)

    def wrapInjectionsInErrorHandling(self, wrap):
        self.logger_everything = wrap(self.logger_everything)

class AddLoggingEverythingModification(ModuleModification):

    def modify(self):
        logging.everything = self.logging_everything

    def logging_everything(self, msg, *args, **kwargs):
        root = logging.Logger.root
        if len(root.handlers) == 0:
            logging.basicConfig()
        root.everything(msg, *args, **kwargs)

    def wrapInjectionsInErrorHandling(self, wrap):
        self.logging_everything = wrap(self.logging_everything)
