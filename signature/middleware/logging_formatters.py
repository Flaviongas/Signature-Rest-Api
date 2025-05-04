import re
import logging

class NoColorFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', message)