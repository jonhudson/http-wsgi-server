import socket
from httpwsgiserver.http.types import ResponseStatus, ResponseHeaders
from typing import cast, Callable

class HttpResponse():
    def __init__(self, socket_handle: socket.socket):
        self.headers_sent = False
        self.socket_handle = socket_handle

    def write_to_stream(self, data):
        if type(data) is str:
            data = data.encode('iso-8859-1', 'replace')

        self.socket_handle.send(data)

    def start_response(self, status: ResponseStatus, 
                        headers: ResponseHeaders) -> Callable[[bytes | str], None]:

        if type(status) is bytes:
            status = status.decode('iso-8859-1')

        self.write_to_stream('HTTP/1.1 ' + cast(str, status) + '\r\n')

        for name, value in headers:
            if type(name) is bytes:
                name = name.decode('iso-8859-1')
            if type(value) is bytes:
                value = value.decode('iso-8859-1')

            self.write_to_stream(cast(str, name) + ': ' + cast(str, value) + '\r\n')
            
        self.write_to_stream('\r\n')
        self.headers_sent = True

        return self.write_to_stream
        



