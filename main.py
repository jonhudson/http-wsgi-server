#!/usr/bin/env python3

import socket
import sys
from httpmessage import parse_message, HttpMessage, get_error_handler
from httpresponse import HttpResponse
from importlib import import_module

wsgi_module_name, wsgi_app_name = sys.argv[1].split(':')
wsgi_module =  import_module(wsgi_module_name)
wsgi_app = getattr(wsgi_module, wsgi_app_name)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('127.0.0.1', 9000))
s.listen()

while True:
    (con_socket, addr) = s.accept()

    message: HttpMessage = parse_message(con_socket)

    environ = {
        'REQUEST_METHOD': message.method,
        'PATH_INFO': message.uri,
        'wsgi.input': message.body,
        'wsgi.errors': get_error_handler(),
        'wsgi.run_once': False,
        'wsgi.multiprocess': False,
        'wsgi.multithread': False,
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': b'http'.decode('iso-8859-1')
    }

    http_resp = HttpResponse(con_socket)

    for data in wsgi_app(environ, http_resp.start_response):
        if http_resp.headers_sent:
            if type(data) is str:
                data = data.encode('iso-8859-1', 'replace')

            con_socket.send(data)

    con_socket.close()


