import logging

from pythonjsonlogger.jsonlogger import JsonFormatter


def init_logger():
    logging.basicConfig(handlers=[logging.StreamHandler()])
    for handler in logging.root.handlers:
        handler.setFormatter(
            JsonFormatter(
                "%(name)s - %(levelname)s - %(message)s",
                rename_fields={"levelname": "severity", "name": "module"},
            )
        )


def get_logger(name: str):
    init_logger()
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger
