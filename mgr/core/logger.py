import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

class LoggerManager:
    def __init__(self, logger_name: str, logger_level: int = logging.WARNING):
        self._logger: logging.Logger = logging.getLogger(logger_name)
        self._logger.setLevel(logger_level)
        self.handlers: dict[str, logging.Handler] = {}

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def set_logger_level(self, level: int):
        self._logger.setLevel(level)

    def add_handler(self,
        name: str,
        handler: logging.Handler,
        level: int = logging.WARNING,
        formatter_string: str = "%(name)s | %(levelname)s | %(message)s"
        ):

        if name in self.handlers:
            raise ValueError(f"A handler named '{name}' already exists.")
        if isinstance(handler, (RotatingFileHandler, logging.FileHandler)):
            log_directory = Path(handler.baseFilename).parent
            os.makedirs(str(log_directory), exist_ok=True)
            

        self.handlers[name] = handler
        self._logger.addHandler(handler)
        self.set_handler_level(name, level)
        self.set_handler_format(name, formatter_string)


    def remove_handler(self, name: str):
        handler = self.handlers.pop(name, None)
        if handler:
            self._logger.removeHandler(handler)
        else:
            self._logger.warning(f"No handler named '{name}' found.")

    def set_handler_level(self, name: str, level: int):
        handler = self.handlers.get(name)
        if handler:
            handler.setLevel(level)
        else:
            self._logger.warning(f"No handler named '{name}' found.")
    
    def set_handler_format(self, name: str, formatter_string: str) -> None:
        handler = self.handlers.get(name)
        formatter = logging.Formatter(formatter_string)
        if handler:
            handler.setFormatter(formatter)
        else:
            self._logger.warning(f"No handler named '{name}' found.")