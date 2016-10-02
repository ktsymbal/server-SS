import mimetypes

CODES = {'200' : 'OK', '404' : 'Not Found', '405' : 'Method Not Allowed',
'400': 'Bad Request'}
DOCS = "www/"

class MyResponse():
    def __init__(self, content_type=None, body=None, version="HTTP/1.1"):
        self.content_type = content_type
        self.body = body
        self.version = version
        self.response = ''

    def generate_response(self, code='400'):
        self.code = code

        self.response = '{} {} {}\r\n'.format(self.version, self.code, CODES[self.code])

        if self.content_type and self.content_type[0]:
            self.response += 'Content-Type : {}'.format(self.content_type[0])

            if self.content_type and self.content_type[1]:
                self.response += '; {}'.format(self.content_type[1])
            self.response += '\r\n'
        if self.body:
                self.response += 'Content-Length : {}\r\nConnection:close\r\n\r\n {}'.format(
                len(self.body), self.body)
        return self.response

    def process_request(self, request):
        if not str(request):
            self.code = '400'
        parsed_request = request.get_parsed_request()
        self.version = parsed_request['version']

        if parsed_request['method'] == 'GET':
            self.GET(parsed_request)
            return self.generate_response()

        self.code = '405'
        self.content_type = ('text/html', None)
        self.body = self.make_body()
        return self.generate_response()

    def GET(self, parsed_request):
        request_url = parsed_request['uri']
        file_name = self.get_file(request_url)
        if file_name:
            self.code = '200'
            self.content_type = mimetypes.guess_type(file_name)
            if self.content_type[0] and self.content_type[0].split('/')[0] == 'text':
                with open(file_name, 'r') as f:
                    self.body = f.read()
            else:
                with open(file_name, 'rb') as f:
                    self.body = f.read()
        else:
            self.code = '404'
            self.body = self.make_body()

    def get_file(self, request_url):
        if request_url == '/':
            return DOCS + 'index.html'
        if request_url == '/file':
            return DOCS + 'file/file.html'
        if request_url == '/obj':
            return DOCS + 'obj/obj.html'

    def make_body(self):
        return '<h1>{} {}</h1>'.format(self.code, CODES[self.code])
