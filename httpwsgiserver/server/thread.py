import socket
from typing import Callable, Iterator
from httpwsgiserver.http.message import (parse_message, HttpMessage, 
        get_error_handler)
from httpwsgiserver.http.response import HttpResponse
from httpwsgiserver.http.types import ResponseStatus, ResponseHeaders

WsgiEnvironDict = dict
WsgiCallable = Callable[
            [
                WsgiEnvironDict, 
                Callable[[ResponseStatus, ResponseHeaders], Callable[[bytes | str], None]]
            ], Iterator
        ]

class Worker():
    def __init__(self, con_socket: socket.socket, 
                 wsgi_app: WsgiCallable) -> None:

        self.wsgi_app = wsgi_app
        self.con_socket = con_socket

        message: HttpMessage = parse_message(self.con_socket)

        server_name, server_port = None, None
        for k, v in message.headers.items():
            if k.lower() == 'host':
                server_name, server_port = v.split(':')
                break

        content_type = None
        for k, v in message.headers.items():
            if k.lower() == 'content-type':
                content_type = v
                break

        content_length = None
        for k, v in message.headers.items():
            if k.lower() == 'content-length':
                content_length = v
                break
        
        environ = {
            'REQUEST_METHOD': message.method,
            'PATH_INFO': message.uri_path,
            'QUERY_STRING': message.uri_query_string,
            'SERVER_PROTOCOL': message.protocol,
            'SERVER_NAME': server_name,
            'SERVER_PORT': server_port,
            'CONTENT_TYPE': content_type,
            'CONTENT_LENGTH': content_length,
            'wsgi.input': message.body,
            'wsgi.errors': get_error_handler(),
            'wsgi.run_once': False,
            'wsgi.multiprocess': False,
            'wsgi.multithread': True,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': b'http'.decode('iso-8859-1')
        } | message.headers

        print(environ)

        http_resp = HttpResponse(self.con_socket)

        for data in self.wsgi_app(environ, http_resp.start_response):
            if http_resp.headers_sent:
                if type(data) is str:
                    data = data.encode('iso-8859-1', 'replace')

                self.con_socket.send(data)

        self.con_socket.close()
