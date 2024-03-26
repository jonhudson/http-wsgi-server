import re
import sys
from typing import Sequence

class HttpMessageBody():
    def __init__(self, body: bytes) -> None:
        self.body = body

    def read(self, size: int) -> bytes:
        if len(self.body) == 0:
            raise IndexError('Already at end of message body')

        chars = self.body[:size] 
        self.body = self.body[size:]

        return chars

    def readline(self) -> bytes:
        if len(self.body) == 0:
            raise IndexError('Already at end of message body')

        ma = re.match(b'.*(\r\n|\r|\n)', self.body)

        if ma is not None:
            line = ma.group(0)
            self.body = self.body[ma.end() + 1:]

            return line

        return b''

    def readlines(self, hint = None):
        if len(self.body) == 0:
            raise IndexError('Already at end of message body')

        lines = re.split(b'(?:\r\n|\r|\n)', self.body)
        self.body = ''
        
        return lines

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.readline()
        except IndexError:
            raise StopIteration


class HttpMessage():

    http_methods = { b'GET', b'PUT', b'POST', b'DELETE', b'HEAD', b'OPTIONS' }

    def __init__(
        self, 
        uri: bytes, 
        method: bytes, 
        protocol: bytes,
        headers: dict[str, str], 
        body: bytes):

        if method not in self.http_methods:
            raise Exception('Invalid HTTP method')

        self.uri = uri.decode('iso-8859-1')

        self.uri_path, self.uri_query_string = self.uri.split('?')

        self.method = method.decode('iso-8859-1')
        self.protocol = protocol.decode('iso-8859-1')
        self.headers = headers
        self.body = HttpMessageBody(body)

class ErrorHandler():
    def flush(self) -> None:
        pass

    def write(self, msg: str) -> None:
        sys.stderr.write(msg)

    def writelines(self, seq: Sequence[str]) -> None:
        for msg in seq:
            sys.stderr.write(msg)

error_handler = None

def get_error_handler():
    global error_handler
    if error_handler is None:
        error_handler = ErrorHandler()

    return error_handler

def parse_message(con_socket):
    """Reads all bytes from socket and returns HttpMessage."""

    # Read some bytes
    message = con_socket.recv(1024)

    # If we haven't got to the end of the header section (which is an empty line)
    # then read some more
    while b'\r\n\r\n' not in message:
        next_chars = con_socket.recv(1024)
        message = message + next_chars


    # Once we have all the headers see if we have a Content-Length header
    length_header_match = re.search(br'Content-Length:\s+(\d+)', message, re.I)

    # If we do, assume we have a body and read that many bytes to end up with 
    # the whole message
    if length_header_match is not None:
        body_len = length_header_match.group(1)
        double_crlf_start = message.find(b'\r\n\r\n')
        body_start = double_crlf_start + 4
        current_body_chars = message[body_start:]

        body_remaining = con_socket.recv(int(body_len) - len(current_body_chars))
        message = message + body_remaining

    # Split the message into header and body sections
    message_parts = re.split(b'\r\n\r\n', message)

    message_header, message_body = message_parts

    # Extract the http method
    method_match = re.match(b'\n*(OPTIONS|GET|HEAD|POST|PUT|DELETE|TRACE|CONNECT)', 
                            message_header)
    method = method_match.group(1)
    next_pos = method_match.end()

    message_header = message_header[next_pos:]

    # Extract the uri
    request_uri_match = re.match(b'\s+([^\s]+)', message_header)
    request_uri = request_uri_match.group(1)
    next_pos = request_uri_match.end()

    message_header = message_header[next_pos:]

    # Extract the protocol
    protocol_match = re.match(b'\s+([^\r\n]+)', message_header)
    protocol = protocol_match.group(1)
    next_pos = protocol_match.end()

    message_header = message_header[next_pos:]

    # Extract the http headers
    headers_pattern = (b'(Accept|Accept-Charset|Accept-Encoding|Accept-Language|'
                          b'Authorization|Expect|From|Host|If-Match|If-Modified-Since|'
                          b'If-None-Match|If-Range|If-Unmodified-Since|'
                          b'Max-Forwards|Proxy-Authorization|Range|Referer|TE|'
                          b'User-Agent|Allow|Content-Encoding|Content-Language|'
                          b'Content-Length|Content-Location|Content-MD5|Content-Range|'
                          b'Content-Type|Expires|Last-Modified):([^\r\n]+)')

    headers_matches = re.findall(headers_pattern, message_header, re.I)

    header_dict = { 
                name.strip().decode('iso-8859-1'): value.strip().decode('iso-8859-1')
                for name, value in headers_matches 
            }

    # Create and return HttpMessage
    message = HttpMessage(request_uri, method, protocol, header_dict, message_body)

    return message
