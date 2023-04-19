import env
from logger.Logger import Logger


class ExecutionDispatch(object):

    LOGGER = Logger.get_logger("ExecutionDispatch")

    @staticmethod
    def run():
        mode = env.RUNTIME_MODE
        if mode == "daemon":
            ExecutionDispatch.LOGGER.info("Running the application in daemon mode")
            from execution.daemon.DaemonExecution import DaemonExecution
            exec = DaemonExecution()
            exec.run()
        elif mode == "classic":
            ExecutionDispatch.LOGGER.info("Running the application in classic mode")
            from execution.classic.ClassicExecution import ClassicExecution
            exec = ClassicExecution()
            exec.run()

