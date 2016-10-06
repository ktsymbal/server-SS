import mimetypes
import re
import disneydb
import json

DIR_URL = lambda dir : '^/{0}$|^/{0}/$'.format(dir)
REC_URL = lambda dir : '^/{0}/([0-9]+)$'.format(dir)

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

        method = parsed_request['method']

        if method == 'GET':
            self.GET(parsed_request)
            return self.generate_response(self.code)

        if method == 'POST':
            self.POST(parsed_request)
            return self.generate_response(self.code)

        if method == 'PUT':
            self.PUT(parsed_request)
            return self.generate_response(self.code)

        if method == 'DELETE':
            self.DELETE(parsed_request)
            return self.generate_response(self.code)

        self.code = '405'
        self.content_type = ('text/html', None)
        self.body = self.make_body()
        return self.generate_response(self.code)

    def GET(self, parsed_request):
        request_url = parsed_request['uri']
        self.code = '200'

        if re.match('/disney/*', request_url):

            if re.match(REC_URL('disney'), request_url):
                id = int(re.findall(REC_URL('disney'), request_url)[0])
                self.body = disneydb.GET(id)

            elif re.match(DIR_URL('disney'), request_url):
                self.body = disneydb.GET_ALL()

            if self.body:
                self.content_type = ('application/json', None)
            else:
                self.code = '404'
                self.body = self.make_body()

        else:
            file_name = self.get_file(request_url)

            if file_name:
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

    def POST(self, parsed_request):
        request_url = parsed_request['uri']

        if re.match(DIR_URL('disney'), request_url):
            try:
                insertion = json.loads(parsed_request['body'])
                if isinstance(insertion, list):
                    disneydb.POST(insertion)
                else:
                    disneydb.POST(insertion)
                self.code = '200'
            except:
                self.code = '400'

    def PUT(self, parsed_request):
        request_url = parsed_request['uri']
        try:
            if re.match(REC_URL('disney'), request_url):
                print "match"
                id = int(re.findall(REC_URL('disney'), request_url)[0])
                update = json.loads(parsed_request['body'])
                disneydb.PUT(update, id)
                self.code = '200'
            else:
                raise BadRequest
        except:
            self.code = '400'

    def DELETE (self, parsed_request):
        request_url = parsed_request['uri']

        if re.match(REC_URL('disney'), request_url):
            id = int(re.findall(REC_URL('disney'), request_url)[0])
            disneydb.DELETE(id)
            self.code = '200'

        else:
            self.code = '400'

    '''
    def POST(self, parsed_request):
        print 'in POST'
        request_url = parsed_request['uri']
        if request_url == '/file' and parsed_request['Content-Type'] and \
            parsed_request['body']:
            try:
                boundary = '--{}--'.format(parsed_request['Content-Type'].split(';')[1].split('=')[1])
            except:
                self.code = '400'
                self.body = make_body()
            with open('file_upload' , 'wb')
            parsed_body = cgi.FieldStorage()
            print parsed_body
            fields = []
            file_itself = {}
            for line in parsed_request['body']:
                if line == boundary:
                    field = {}
                else:
                    header = line.split(':', 1)
    '''


    def get_file(self, request_url):
        if request_url == '/':
            return DOCS + 'index.html'
        if re.match(DIR_URL('file'), request_url):
            return DOCS + 'file/file.html'
        if re.match(DIR_URL('obj'), request_url):
            return DOCS + 'obj/obj.html'

    def make_body(self):
        return '<h1>{} {}</h1>'.format(self.code, CODES[self.code])
