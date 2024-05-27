import logging

from pythonjsonlogger.jsonlogger import JsonFormatter


logging.basicConfig(handlers=[logging.StreamHandler()])
for handler in logging.root.handlers:
    format_ = "%(name)s - %(levelname)s - %(message)s"
    rename_fields = {"levelname": "severity", "name": "module"}
    handler.setFormatter(JsonFormatter(format_, rename_fields))


def get_logger(module_name: str):
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    return logger
