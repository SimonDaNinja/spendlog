import os

class ModuleModder:

    def __init__(self, modifications):
        self.modifications = modifications
        self.executeAllModifications()

    def executeAllModifications(self):
        for modification in self.modifications:


            doBeforeModify = self.wrapModifyInErrorHandling(modification.doBeforeModify)
            doBeforeModify()

            modification.wrapInjectionsInErrorHandling(self.wrapInjectionInErrorHandling)

            self.addRestoreStepToHandling(modification.restore)
            modify = self.wrapModifyInErrorHandling(modification.modify)

            if not modify():
                return

    def wrapModifyInErrorHandling(self, func):
        def wrapped(*args, **kwargs):
            try:
                func(*args, **kwargs)
                return True
            except Exception as e:
                self.handleError(e)
                return False
        return wrapped

    def wrapInjectionInErrorHandling(self, func, recoverFun):
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.handleError(e)
                # if the function we injected fails inside the modded module, the modded module
                # is still going to expect a valid return value. recoverFun will safely provide this
                return recoverFun(*args, **kwargs)
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


class ModuleModification:

    def doBeforeModify(self):
        pass

    def modify(self):
        pass

    def restore(self):
        pass

    def wrapInjectionsInErrorHandling(self, wrap):
        pass

# The remaining code is for adding the log level EVERYTHING to the logging module
# (a severity level more verbose than DEBUG)

import logging
EVERYTHING = 1

class AddTraceLevelEverythingModder(ModuleModder):
    def __init__(self):
        super().__init__(
            [
                AddFallbackToDebugMod(),
                ReplaceIsInternalFrameMod(),
                AddLevelEverythingMod(),
                AddLoggerEverythingMod(),
                AddLoggingEverythingMod()
            ]
        )

    def handleError(self, e):
        logging.error(f'Failed to define logging level EVERYTHING with the following exception:\n\n"{e}"\n\nUsing DEBUG level for EVERYTHING level prints instead')


class AddFallbackToDebugMod(ModuleModification):

    def restore(self):
        logging.Logger.everything = logging.Logger.debug
        logging.EVERYTHING = logging.DEBUG
        logging.everything = logging.debug


class ReplaceIsInternalFrameMod(ModuleModification):

    def doBeforeModify(self):
        self._is_internal_frame_original = logging._is_internal_frame

    def restore(self):
        logging.is_internal_frame = self._is_internal_frame_original

    def modify(self):
        logging._is_internal_frame = self._is_internal_frame_replacement

    def _is_internal_frame_replacement(self, frame):
        thisfile = os.path.normcase(self.restore.__code__.co_filename)
        filename = os.path.normcase(frame.f_code.co_filename)
        if thisfile == filename:
            return True
        return self._is_internal_frame_original(frame)

    def wrapInjectionsInErrorHandling(self, wrap):
        self._is_internal_frame_replacement = wrap(self._is_internal_frame_replacement, self._is_internal_frame_original)

class AddLevelEverythingMod(ModuleModification):

    def modify(self):
        logging.EVERYTHING = EVERYTHING
        logging.addLevelName(logging.EVERYTHING, "EVERYTHING")

class AddLoggerEverythingMod(ModuleModification):

    def modify(self):
        logging.Logger.everything = self.logger_everything

    def logger_everything(self, loggerSideSelf, msg, *args, **kwargs):
        if loggerSideSelf.isEnabledFor(EVERYTHING):
            loggerSideSelf._log(EVERYTHING, msg, args, **kwargs)

    def wrapInjectionsInErrorHandling(self, wrap):
        self.logger_everything = wrap(self.logger_everything, logging.Logger.debug)

class AddLoggingEverythingMod(ModuleModification):

    def modify(self):
        logging.everything = self.logging_everything

    def logging_everything(self, msg, *args, **kwargs):
        root = logging.Logger.root
        if len(root.handlers) == 0:
            logging.basicConfig()
        root.everything(msg, *args, **kwargs)

    def wrapInjectionsInErrorHandling(self, wrap):
        self.logging_everything = wrap(self.logging_everything, logging.debug)
