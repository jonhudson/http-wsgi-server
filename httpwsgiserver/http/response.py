import socket
from httpwsgiserver.http.types import ResponseStatus, ResponseHeaders

class HttpResponse():
    def __init__(self, socket_handle: socket):
        self.headers_sent = False
        self.socket_handle = socket_handle

    def write_to_stream(self, data: bytes | str):
        if type(data) is str:
            data = data.encode('iso-8859-1', 'replace')

        self.socket_handle.send(data)

    def start_response(self, status: ResponseStatus, 
                        headers: ResponseHeaders) -> None:

        if type(status) is bytes:
            status = status.decode('iso-8859-1')

        self.write_to_stream('HTTP/1.1 ' + status + '\r\n')

        for name, value in headers:
            if type(name) is bytes:
                name = name.decode('iso-8859-1')
            if type(value) is bytes:
                value = value.decode('iso-8859-1')

            self.write_to_stream(name + ': ' + value + '\r\n')
            
        self.write_to_stream('\r\n')
        self.headers_sent = True

        return self.write_to_stream
        



