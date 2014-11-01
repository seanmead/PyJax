"""
Created on Oct 1, 2014

@author: Sean Mead
"""

from python.modules import Settings, Tools
from python.modules.Client import Client
import os
import threading
import time
import socket
import ssl
import hashlib
import base64
import BaseHTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler


SockKey = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


class Req(object):
    def __init__(self):
        """
        Create a Req object.  The object holds arguments as a dictionary and a request path.
        """
        self.__path = ''
        self.__method = ''
        self.__arguments = {}

    @property
    def path(self):
        """
        :return: The path of the request
        """
        return self.__path

    @path.setter
    def path(self, path):
        self.__path = path

    @property
    def method(self):
        """
        :return: The method of the request
        """
        return self.__method

    @method.setter
    def method(self, method):
        self.__method = method

    @property
    def arguments(self):
        """
        :return: The request arguments
        """
        return self.__arguments


class ClientHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, data):
        """
        Handler for the requests from the Server
        :param request:
        :param client_address:
        :param data:
        """
        BaseHTTPRequestHandler.__init__(self, request, client_address, data)
        self.__req = Req()
        self.__tmp = None
        self.__cookies = {}
        self.__header_count = 0
        self.__headers_send = []

    @property
    def tmp(self):
        """
        The tmp file location if triggered from file upload
        :return: The name of the tmp file.
        """
        return self.__tmp

    @property
    def req(self):
        """
        The req object containing the request information.
        :rtype : Req
        :return: req
        """
        return self.__req

    @req.setter
    def req(self, req):
        self.__req = req

    def address_string(self):
        """
        Override the built in address_string() to return the address.
        """
        return '%s:%s' % self.client_address

    def do_GET(self):
        """
        Called when a get request is triggered.
        Receives arguments, and triggers Client() get.
        """
        self.__receive()
        self.req.method = "GET"
        Client(self).get()

    def do_POST(self):
        """
        Called when a post request is triggered.
        Receives arguments, checks content length and triggers Client() post.
        """
        self.__receive()
        self.req.method = "POST"
        length = long(self.headers.getheader('content-length'))
        line, index = self.__receive_line(length)
        if index < length:
            self.__read_file(line, length - index)
        self.__read_arguments(line)
        Client(self).post()

    def __read_file(self, line, length):
        """
        Reads the file that is uploaded into a temp directory.
        :param line: First line of the file
        :param length:  Length of the content
        """
        self.__tmp = Settings.Settings.WORKING_DIR + '/tmp/' + str(time.time())
        with open(self.__tmp, 'wb') as o:
            o.write(line)
        max_int = 100000000
        loop = length/max_int
        m = length % max_int
        for i in range(0, loop):
            with open(self.__tmp, 'ab') as o:
                o.write(self.rfile.read(max_int))
        with open(self.__tmp, 'ab') as o:
                o.write(self.rfile.read(m))

    def move_tmp(self, path):
        """
        Moves the tmp file to the specified path.
        :param path: directory to move the tmp file to
        :return: name of the file
        """
        if self.__tmp:
            h = open(self.__tmp, 'rb')
            boundary = h.readline()
            filename = Tools.get_item(h.readline(), 'filename')[1:-1]
            content_type = h.readline().split(': ')[-1]
            blank_line = h.readline()
            with open(path + filename, 'wb') as o:
                o.writelines(h.readlines()[:-1])
            h.close()
            os.remove(self.__tmp)
            return filename

    def write(self, content):
        """
        Sends the content to the client with headers.
        :param content: Content to send
        """
        if self.__header_count == 0:
            self.set_header('Content-Type', 'text/html')
        self.wfile.write('HTTP/1.0 200 OK\r\n%s\r\n' % ''.join(self.__headers_send))
        self.wfile.write(str(content))

    def set_cookie(self, name, value):
        """
        Add cookie header with the name, value.
        :param name: Name of the cookie
        :param value: Value of the cookie
        """
        self.set_header('Set-Cookie', '%s=%s; Expires=Wed, 09 Jun 2021 10:18:14 GMT' % (name, value))

    def set_header(self, name, value):
        """
        Add a header with name, value
        :param name: Name of the header
        :param value: Value of the header
        """
        self.__header_count += 1
        self.__headers_send.append('%s: %s\r\n' % (name, value))

    def get_argument(self, name):
        """
        Convenience method to access handler arguments.
        :param name: Name of the argument
        :return: Value of the argument
        """
        return self.req.arguments.get(name)

    def get_cookie(self, name):
        """
        Get the value of a cookie
        :param name: Name of the cookie to get
        :rtype : string
        """
        return self.__cookies.get(name)

    def __read_cookies(self):
        """
        Read in the cookies for the constructed headers.
        """
        cookies = self.headers.getheader('cookie')
        if cookies:
            cookies = cookies.split(';')
            for cookie in cookies:
                name, value = cookie.strip().split('=', 2)
                self.__cookies.update({name: value})

    def __build_socket_headers(self):
        """
        Build the socket headers.
        """
        self.set_header('Upgrade', self.headers.getheader('upgrade'))
        self.set_header('Connection', self.headers.getheader('Connection'))
        self.set_header('Sec-WebSocket-Protocol', self.headers.getheader('Sec-WebSocket-Protocol'))
        key = self.headers.getheader('Sec-WebSocket-Key')
        if key:
            self.set_header('Sec-WebSocket-Accept', base64.b64encode(hashlib.sha1(key + SockKey).digest()))

    def __read_arguments(self, line):
        """
        Read arguments for the current line.
        """
        args = line.split('&')
        for arg in args:
            if '=' in arg:
                name, value = arg.split('=')
                self.req.arguments.update({Tools.strip_item(name.strip()): Tools.strip_item(value.strip())})

    def __receive_line(self, length):
        """
        Receive a single line from the client.
        :return: The entire line, index of line.
        """
        line = ''
        char = ''
        index = 0
        while char != '\n' and index < length:
            char = self.rfile.read(1)
            line += char
            index += 1
        return line, index

    def __receive(self):
        """
        Do all receive
        """
        self.req = Req()
        self.__tmp = None
        self.__cookies = {}
        self.__header_count = 0
        self.__headers_send = []
        path = self.path.split('?')
        self.req.path = path[0]
        if len(path) == 2:
            self.__read_arguments(path[1])
        self.__read_cookies()


class SocketHandler(threading.Thread):
    def __init__(self, connection):
        """
        Handler for requests from the WebSocketServer
        :param connection: Socket
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.__connection = connection
        self.__req = Req()
        self.__headers = {}
        self.__cookies = {}
        self.__header_count = 0
        self.__headers_send = []

    @property
    def connection(self):
        return self.__connection

    @property
    def req(self):
        return self.__req

    def run(self):
        self.__receive()

    def get_cookie(self, name):
        return self.__cookies.get(name)

    def set_cookie(self, name, value):
        self.set_header('Set-Cookie', '%s=%s; Expires=Wed, 09 Jun 2021 10:18:14 GMT' % (name, value))

    def get_argument(self, name):
        return self.req.arguments.get(name)

    def set_header(self, name, value):
        self.__header_count += 1
        self.__headers_send.append('%s: %s\r\n' % (name, value))

    def write(self, content):
        self.__build_socket_headers()
        self.__connection.send('HTTP/1.1 101 Switching Protocols\r\n%s\r\n' % ''.join(self.__headers_send))
        self.__connection.setblocking(0)

    def __read_cookies(self):
        if 'Cookie' in self.__headers:
            cookies = self.__headers.get('Cookie')
            if cookies:
                cookies = cookies.split(';')
                for cookie in cookies:
                    name, value = cookie.strip().split('=', 2)
                    self.__cookies.update({name: value})

    def __read_arguments(self, line):
        args = line.split('&')
        for arg in args:
            if '=' in arg:
                name, value = arg.split('=')
                self.req.arguments.update({Tools.strip_item(name.strip()): Tools.strip_item(value.strip())})

    def __build_socket_headers(self):
        self.set_header('Upgrade', self.__headers.get('Upgrade'))
        self.set_header('Connection', self.__headers.get('Connection'))
        self.set_header('Sec-WebSocket-Protocol', self.__headers.get('Sec-WebSocket-Protocol'))
        key = self.__headers.get('Sec-WebSocket-Key')
        if key:
            self.set_header('Sec-WebSocket-Accept', base64.b64encode(hashlib.sha1(key + SockKey).digest()))

    def __receive_line(self):
        line = ''
        char = ''
        while char != '\n':
            char = self.__connection.recv(1)
            line += char
        return line

    def __receive(self):
        method, path, protocol = self.__receive_line().split(' ', 3)
        path = path.split('?')
        self.req.path = path[0]
        if len(path) == 2:
            self.__read_arguments(path[1])
        line = ':'
        while ':' in line:
            line = self.__receive_line()
            if ':' in line:
                name, value = line.split(':', 1)
                self.__headers.update({name.strip(): value.strip()})
        self.__read_cookies()
        Client(self).socket()


class WebSocketServer(threading.Thread):
    def __init__(self):
        """
        WebSocketServer object is used to host the SocketServer.  No parameters are needed.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__cert = Settings.get('cert')

    @property
    def server(self):
        return self.__server

    def run(self):
        try:
            self.__server.bind((Settings.get('address'), Settings.get('socketport')))
        except Exception:
            pass
        while True:
            try:
                self.__server.listen(50)
                connection, address = self.__server.accept()
                if self.__cert:
                    connection = ssl.wrap_socket(connection, certfile=self.__cert, server_side=True)
                SocketHandler(connection).start()
            except Exception:
                pass


class WebServer(BaseHTTPServer.HTTPServer):
    def __init__(self, args, handler):
        """
        Overrides the BaseHTTPServer to respond cleaner.
        :param args:
        :param handler:
        """
        BaseHTTPServer.HTTPServer.__init__(self, args, handler)
        self.__running = True

    @property
    def running(self):
        return self.__running

    @running.setter
    def running(self, run):
        self.__running = run

    def serve_forever(self, poll_interval=0.5):
        while self.running:
            self.handle_request()
        self.socket.close()


class Server(threading.Thread):
    def __init__(self):
        """
        Server object is used to host the normal WebServer.  No parameters are needed.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.__server = WebServer((Settings.get('address'), Settings.get('port')), ClientHandler)
        self.__server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server.allow_reuse_address = socket.SO_REUSEADDR
        cert = Settings.get('cert')
        if cert:
            self.__server.socket = ssl.wrap_socket(self.__server.socket, certfile=cert, server_side=True)
        self.__running = True

    @property
    def server(self):
        return self.__server

    @property
    def running(self):
        return self.__running

    @running.setter
    def running(self, running):
        self.__running = running

    def run(self):
        self.__server.serve_forever(0)
