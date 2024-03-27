import socket
import sys
import logging
from importlib import import_module
from threading import Thread
from httpwsgiserver.server.thread import Worker

#TODO allow setting from command args
loglevel = 'debug' 
numeric_level = getattr(logging, loglevel.upper(), None)

if not isinstance(numeric_level, int):
    raise ValueError(f'Invalid log level: {loglevel}')

logging.basicConfig(level=numeric_level)
logger = logging.getLogger(__name__)

wsgi_module_name, wsgi_app_name = sys.argv[2].split(':')
wsgi_module =  import_module(wsgi_module_name)
wsgi_app = getattr(wsgi_module, wsgi_app_name)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host, port = sys.argv[1].split(':')

s.bind((host, int(port)))
s.listen()

threads = []

while True:
    (con_socket, addr) = s.accept()

    t = Thread(target=Worker, args=(con_socket, wsgi_app, logger))
    threads.append(t)
    t.start()
    t.join()
