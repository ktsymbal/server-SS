import sys
import getopt
import time
import socket
import argparse
import mimetypes

class Server():
    def __init__(self, argv):
        self.host, self.port = self.parse_argv(argv)
        self.s = socket.socket()
        self.fs = "www/"
        self.access =  'access.log'
        self.error = 'error.log'
        f = open(self.access, 'w')
        f.close()
        f = open(self.error, 'w')
        f.close()

    def recv_request(self, sock, timeout=2, delim='\r\n\r\n', bufsize=4096):
        '''
        :return: tuple (request, parsed_request)
        request is a string
        parsed_request is a dictionary ({'method' : method, 'uri' : uri, 'version': version,
        ['header' : value], ['body': body]})
        '''
        sock.settimeout(timeout)
        data = ''
        try:
            while True:
                rdata = sock.recv(bufsize)
                if rdata:
                    if delim in rdata:
                        pos_delim = rdata.find(delim)
                        till_delim = data + rdata[:pos_delim]
                        data += rdata
                        after_delim = rdata[pos_delim + len(delim):]
                        parsed_request = self.parse_headers(till_delim)
                        if not parsed_request:
                            return ('', {})
                        if 'Content-Length' in parsed_request.keys() and parsed_request['Content-Length'] > '0':
                            rdata = sock.recv(int(parsed_request['Content-Length']) - len(after_delim))
                            data += rdata
                            parsed_request['body'] = after_delim + rdata
                        break
                    data += rdata
                else:
                    time.sleep(0.1)
            return data, parsed_request
        except socket.timeout:
            error = open(self.error, 'a')
            error.write('\n')
            error.close()
            sock.close()

    def connection(self):
        self.s.bind((self.host, self.port))
        print 'Listening to {}:{}'.format(self.host, self.port)
        self.s.listen(1)
        while True:
            access = open(self.access, 'a')
            connection, address = self.s.accept()
            access.write('Connected to {}:{}\n'.format(self.host, self.port))
            request = self.recv_request(connection)
            if request:
                access.write(request[0])
                response = self.process_request(request[1])
                access.write(response)
                connection.sendall(response)
                connection.close()
            access.write('Connection closed\n')
            access.close()

    def parse_headers(self, part_request):
        '''
        :part_request: request line and headers of the request as a string
        :return: parsed request line and headers as
                    {'method' : method, 'uri' : uri, 'version': version,
                    'header 1' : value, ...} in case of success
                None otherwise
        '''
        request = {}
        lines = part_request.split('\r\n')
        if not lines[0]:
            return None
        request_line = lines[0].split(' ')
        if not len(request_line) == 3:
            return None
        request['method'] = request_line[0]
        request['uri']  = request_line[1]
        request['version'] =  request_line[2]
        for header in lines[1:]:
            header_split = header.split(':', 1)
            if not len(header_split) == 2:
                return None
            request[header_split[0]] = header_split[1]
        return request

    def process_request(self, parsed_request):
        if not parsed_request:
            return self.generate_response('400')
        if parsed_request['method'] == 'GET':
            for_response = self.GET(parsed_request)
            return self.generate_response(for_response[0], for_response[1], for_response[2], parsed_request['version'])
        return self.generate_response('405', ('text/html', None ), '<h1>405 Method Not Allowed</h1>', parsed_request['version'])

    def GET(self, parsed_request):
        request_url = parsed_request['uri']
        file_name = self.get_file(request_url)
        if file_name:
            code = '200'
            content_type = mimetypes.guess_type(file_name)
            if content_type[0] and content_type[0].split('/')[0] == 'text':
                body = open(file_name, 'r').read()
            else:
                body = open(file_name, 'rb').read()
            return [code, content_type, body]
        code = '404'
        body = '<h1>404 NOT FOUND</h1>'
        return [code, ('text/html', None ), body]

    def generate_response(self, code, content_type=None, body=None, version="HTTP/1.1"):
        codes = {'200' : 'OK', '404' : 'Not Found', '405' : 'Method Not Allowed',
        '400': 'Bad Request'}
        response = version + ' ' + code + ' ' +codes[code] + '\r\n'
        if content_type and content_type[0]:
            response += 'Content-Type : ' + content_type[0]
            if content_type and content_type[1]:
                response += ';' + content_type[1]
            response += '\r\n'
        if body:
                response += 'Content-Length : ' + str(len(body)) + '\nConnection : close \r\n\r\n' + str(body)
        return response

    def get_file(self, request_url):
        if request_url == '/':
            return self.fs + 'index.html'
        if request_url == '/file':
            return self.fs + 'file/file.html'
        if request_url == '/obj':
            return self.fs + 'obj/obj.html'

    def parse_argv(self, arg):
        host = ''
        port = ''
        argv = arg[1:]
        try:
            opts, args = getopt.getopt(argv,"h:p:s:")
        except getopt.GetoptError as err:
            print str(err)
        try:
            for opt, argument in opts:
                if opt == '-s':
                    if not len(opts) == 1:
                        raise ValueError
                    sock = argument.split(':')
                    if not len(sock) == 2:
                        raise ValueError
                    host = sock[0]
                    port = sock[1]
                elif opt == '-h':
                    host = argument
                elif opt == '-p':
                    port = argument
            if not (host and port):
                raise ValueError
            return host, int(port)
        except:
            print 'usage 1: python ' + arg[0] + '-h <host name> -p <port name>'
            print 'usage 2: python ' + arg[0] + '-s <host name>:<port name>'
            sys.exit(1)


if __name__ == '__main__':
    server = Server(sys.argv)
    server.connection()
