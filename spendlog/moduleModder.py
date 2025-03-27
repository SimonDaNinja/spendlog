import os

# A class for safely modifying an existing module, and recovering if modification of the
# module fails
class ModuleModder:

    def __init__(self, modifications):
        self.modifications = modifications
        self.executeAllModifications()

    def executeAllModifications(self):
        for modification in self.modifications:

            doBeforeModify = self.wrapModifyInErrorHandling(modification.doBeforeModify)
            if not doBeforeModify():
                return

            modification.wrapPayloadInErrorHandling(self.wrapPayloadInErrorHandling)

            self.addRestoreStepToHandling(modification.restore)

            modify = self.wrapModifyInErrorHandling(modification.modify)

            if not modify():
                return

    # This is distinct from wrapPayloadInErrorHandling!
    # wrapModifyInErrorHandling handles errors caused when trying to insert the payload, and needs
    # to return a bool that indicates whether to abort further steps in the modification procedure
    def wrapModifyInErrorHandling(self, func):
        def wrapped(*args, **kwargs):
            try:
                func(*args, **kwargs)
                return True
            except Exception as e:
                self.handleError(e)
                return False
        return wrapped

    # This is distinct from wrapModifyInErrorHandling!
    # wrapPayloadInErrorHandling handles runtime errors caused by the payload *after* succesfully inserting it,
    # and needs to return context relevant output to not cause a crash
    def wrapPayloadInErrorHandling(self, func, recoverFun):
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.handleError(e)
                # if the function we injected fails inside the modded module, the modded module
                # is still going to expect a valid return value. recoverFun will safely provide this.
                # (this is separate from the purpose of handleError, which has the purpose of recovering
                # the module itself to a stable state)
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

    def wrapPayloadInErrorHandling(self, wrap):
        pass

# The remaining code is for adding the log level EVERYTHING to the logging module
# (a severity level more verbose than DEBUG)

import logging

# EVERYTHING is supposed to be the lowest severity level possible
EVERYTHING = 1

# This modder injects the new severity level EVERYTHING to the logging module.
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


# Since the code base makes use of logging.everything(), we need a step to provide this
# symbol even if the modification failed. This Mod simply sets the necessary symbols
# to use the existing debug level if these symbols are used (so we aren't strictly
# restoring the module entirely, because that would cause us to crash when these calls
# inevitably happen)
class AddFallbackToDebugMod(ModuleModification):

    def restore(self):
        logging.Logger.everything = logging.Logger.debug
        logging.EVERYTHING = logging.DEBUG
        logging.everything = logging.debug

# Since the payloads we inject from this file are not internal to the logging module,
# the funcName formatting will not show the file calling logging.everythin() by
# default, but instead it will show this file. To avoid this, we complement logging's
# check of whether a frame is internal, to first check if it is a frame from this file.
# If it is, we count it as internal. Otherwise, we proceed to the original check defined
# inside the logging module.
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

    def wrapPayloadInErrorHandling(self, wrap):
        self._is_internal_frame_replacement = wrap(self._is_internal_frame_replacement, self._is_internal_frame_original)

# This simply adds the constant EVERYTHING to the logging module, so it can be
# used similar to DEBUG, WARNING, etc. when configuring log severity level
class AddLevelEverythingMod(ModuleModification):

    def modify(self):
        logging.EVERYTHING = EVERYTHING
        logging.addLevelName(logging.EVERYTHING, "EVERYTHING")

# This injects the logging function logging.Logger.everything(), by the same principle
# (and design) as logging's internal corresponding functions logging.Logger.debug(),
# logging.Logger.warning(), etc.
class AddLoggerEverythingMod(ModuleModification):

    def modify(self):
        logging.Logger.everything = self.logger_everything

    def logger_everything(self, loggerSideSelf, msg, *args, **kwargs):
        if loggerSideSelf.isEnabledFor(EVERYTHING):
            loggerSideSelf._log(EVERYTHING, msg, args, **kwargs)

    def wrapPayloadInErrorHandling(self, wrap):
        self.logger_everything = wrap(self.logger_everything, logging.Logger.debug)

# This injects the logging function logging.everything(), by the same principle
# (and design) as logging's internal corresponding functions logging.debug(),
# logging.warning(), etc.
class AddLoggingEverythingMod(ModuleModification):

    def modify(self):
        logging.everything = self.logging_everything

    def logging_everything(self, msg, *args, **kwargs):
        root = logging.Logger.root
        if len(root.handlers) == 0:
            logging.basicConfig()
        root.everything(msg, *args, **kwargs)

    def wrapPayloadInErrorHandling(self, wrap):
        self.logging_everything = wrap(self.logging_everything, logging.debug)
