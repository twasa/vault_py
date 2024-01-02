import logging
from datetime import datetime
from python_libs import json_logger

class CustomJsonFormatter(json_logger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

class Jloger:
    _instance = None
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)


    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance.logger
