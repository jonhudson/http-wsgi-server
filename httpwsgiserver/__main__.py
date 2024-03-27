import socket
import sys
from importlib import import_module
from threading import Thread
from httpwsgiserver.server.thread import Worker

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

    t = Thread(target=Worker, args=(con_socket, wsgi_app))
    threads.append(t)
    t.start()
    t.join()
