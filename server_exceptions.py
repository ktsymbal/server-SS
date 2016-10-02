class BadRequest(Exception):
    def __init__(self):
        self.code = '400'

    def __str__(self):
        return 'Bad Request'

class NotFound(Exception):
    def __init__(self):
        self.code = '404'

    def __str__(self):
        return 'Not Found'

class MethodNotAllowed(Exception):
    def __init__(self):
        self.code = '405'

    def __str__(self):
        return 'Method Not Allowed'
