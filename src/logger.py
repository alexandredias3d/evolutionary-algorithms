import logging
from datetime import datetime

def get_logger(name):
	''' Return the logger object with the provided configuration. '''

	logging.basicConfig(level=logging.DEBUG,
                     format='{asctime}\t[{name:<18}:{levelname:<8}]:\t{message:<}',
			    style='{',
			    filename=datetime.now().strftime('log/%Y-%m-%d---%H-%M-%S') + '.log',
                            filemode='a')
	return logging.getLogger(name)
