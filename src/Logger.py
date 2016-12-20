import logging

import os
import datetime

from config import settings

logLevels = {
	'Critical': logging.CRITICAL,
	'Error': logging.ERROR,
	'Warning': logging.WARNING,
	'Info': logging.INFO,
	'Debug': logging.DEBUG,
}

class LogFormatter(logging.Formatter):
	def format(self, record):
		thisPath = os.path.dirname(__file__)
		if record.pathname.find(thisPath) == 0:
			record.pathname = record.pathname[len(thisPath)+1:]

		if isinstance(record.msg, str):
			record.msg = record.msg.replace("\n", "\\n")

		formatted = super().format(record)
		#print(formatted)
		print(record.msg)
		
		return formatted

if not os.path.exists('logs'):
    os.makedirs('logs')

logger = logging.getLogger('')

logger.setLevel(logLevels[settings.value('logLevel', 'Debug')])
handler = logging.FileHandler(os.path.join('logs', '{0:%Y-%m-%d_%H%M%S}.log'.format(datetime.datetime.now())))
handler.setFormatter(LogFormatter('[%(levelname)-8s] [%(asctime)s] [%(pathname)40s:%(lineno)3s - %(funcName)24s] %(message)s'))
logger.addHandler(handler)
