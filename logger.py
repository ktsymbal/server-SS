ACCESS_FILE = 'access.log'
ERROR_FILE = 'error.log'

class Logger():
    def __init__(self):
        #clear log files
        with open(ACCESS_FILE, 'w'), open(ERROR_FILE, 'w'):
            pass

    def access_logger(self, msg):
        with open(ACCESS_FILE, 'a') as access:
            access.write(msg);

    def error_logger(self, msg):
        with open(ERROR_FILE, 'a') as error:
            error.write(msg);
