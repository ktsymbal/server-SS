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

    def connection(self):
        self.s.bind((self.host, self.port))
        print 'Listening to {}:{}'.format(self.host, self.port)
        self.s.listen(1)
        while True:
            access = open(self.access, 'a')
            connection, address = self.s.accept()
            access.write('Connected to {}:{}\n'.format(self.host, self.port))
            request = connection.recv(1024)
            #request = self.recv_timeout(connection)
            if request:
                access.write(request + '\n')
                response = self.parse_request(request)
                access.write(response)
                connection.sendall(response)
                connection.close()
            access.write('Connection closed\n')
            access.close()

    def parse_request(self, request):
        request_lines = [line.rstrip('\r') for line in request.split('\n')]
        request_line = request_lines[0].split(' ')
        if request_line[0] == 'GET':
            for_response = self.GET(request_line)
            return self.generate_response(request_line[-1], for_response[0], for_response[1], for_response[2])
        return self.generate_response(request_line[-1], '405', None, '<h1>405 Method Not Allowed</h1>')

    def GET(self, request_line):
        request_url = request_line[1]
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
        return [code, None, body]

    def generate_response(self, version, code, content_type, body):
        codes = {'200' : 'OK', '404' : 'Not Found', '405' : 'Method Not Allowed'}
        response = version + ' ' + code + ' ' +codes[code] + '\n'
        if content_type and content_type[0]:
            response += 'Content-Type : ' + content_type[0] + '\n'
        if content_type and content_type[1]:
            response += content_type[1] + '\n'
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
