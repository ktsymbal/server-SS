from server_exceptions import *
import sys, getopt, time, socket, mimetypes
from logger import Logger
from myresponse import MyResponse
from myrequest import MyRequest

class Server():
    def __init__(self, argv):
        self.host, self.port = self.parse_argv(argv)
        self.s = socket.socket()
        self.log = Logger()

    def recv_request(self, sock, timeout=2, delim='\r\n\r\n', bufsize=4096):
        '''
        :return: tuple (request, parsed_request)
        request is a string
        parsed_request is a dictionary ({'method' : method, 'uri' : uri, 'version': version,
        ['header' : value], ['body': body]})
        '''
        sock.settimeout(timeout)
        data = ''
        request = MyRequest()

        try:
            while True:
                rdata = sock.recv(bufsize)

                if rdata:
                    if delim in rdata:
                        pos_delim = rdata.find(delim)
                        data += rdata[:pos_delim]
                        after_delimeter = rdata[pos_delim + len(delim):]
                        try:
                            request.parse_headers(data)
                        except (BadRequest, MethodNotAllowed, NotFound):
                            self.log.access_logger(data)
                            raise
                        parsed_request = request.get_parsed_request()

                        if ('Content-Length' in parsed_request.keys() and
                             parsed_request['Content-Length'] > '0'):

                            rdata = sock.recv(
                            int(parsed_request['Content-Length']) - len(after_delim))
                            request.parse_body(after_delim + rdata)
                        break

                    data += rdata
                else:
                    time.sleep(0.1)
            return request
        except socket.timeout:
            self.log.error_logger('Timeout')
            sock.close()

    def connection(self):
        self.s.bind((self.host, self.port))
        print 'Listening to {}:{}'.format(self.host, self.port)
        self.s.listen(1)

        while True:
            connection, address = self.s.accept()
            self.log.access_logger('Connected to {}:{}\n'.format(self.host, self.port))
            response = MyResponse()
            resp = ''

            try:
                req = self.recv_request(connection)
                self.log.access_logger('\n' + str(req) + '\n')
                resp = response.process_request(req)
            except (BadRequest, NotFound, MethodNotAllowed) as e:
                resp = response.generate_response(e.code)
            finally:
                self.log.access_logger(resp)
                self.log.access_logger('\nConnection closed\n\n')
                connection.sendall(resp)
                connection.close()

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
