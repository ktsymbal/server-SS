from server_exceptions import *
import re

METHODS = ('GET')

class MyRequest():
    def __init__(self):
        '''
        :request: is a string
        :parsed_request: is a dictionary {'method' : method, 'uri' : uri, 'version': version,
        'header' : value, 'body': body}
        '''
        self.request = ''
        self.parsed_request = {}

    def get_parsed_request(self):
        return self.parsed_request

    def parse_headers(self, part_request):
        print self.request
        self.request = part_request

        lines = part_request.split('\r\n')
        print 'lines {}'.format(lines)

        if not lines[0]:
            raise BadRequest
        request_line = lines[0].split(' ')
        if not len(request_line) == 3:
            raise BadRequest

        self.parsed_request['method'] = request_line[0]

        if not self.parsed_request['method'] in METHODS:
            raise MethodNotAllowed

        self.parsed_request['uri']  = request_line[1]
        self.parsed_request['version'] =  request_line[2]

        try:
            if not (re.match('HTTP/1.0|HTTP/1.1',
            self.parsed_request['version']) and len(self.parsed_request['version']) == 8):
                print self.parsed_request['version']
                print len(self.parsed_request['version'])
                raise BadRequest
        except BadRequest:
            raise

        for header in lines[1:]:
            header_split = header.split(':', 1)
            self.parsed_request[header_split[0]] = header_split[1]

    def parse_body(body):
        self.request += body
        self.parsed_request['body'] = body

    def __str__(self):
        return self.request
