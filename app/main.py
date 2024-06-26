from io import StringIO
import io
import socket
import socketserver
from time import time

from app.key_value_store import KeyValueStore
from app.resp import BulkString, ErrorString, NilBulkString, RESPArray, RESPValue, SimpleString, parse_resp_value, serialize_resp_value


key_store = KeyValueStore()


def print_prefix_lines(text: str, prefix: str):
    print(*(prefix + line for line in text.splitlines()), sep="\n")


def execute_command(query: list[str]) -> RESPValue:
    command = query[0].upper()
    match (command, query[1:]):
        case ("PING", []):
            return SimpleString("PONG")
        case ("PING" | "ECHO", [arg]):
            return BulkString(arg)
        case ("SET", [key, value, *options]):
            option_name = options[0].upper() if options else None
            match (option_name, options[1:]):
                case (None, _):
                    expires_at = None
                case ("EX", [seconds]):
                    expires_at = int(time() * 1000) + int(seconds) * 1000
                case ("PX", [milliseconds]):
                    expires_at = int(time() * 1000) + int(milliseconds)
                case ("EXAT", [timestamp]):
                    expires_at = int(timestamp) * 1000
                case ("PXAT", [timestamp]):
                    expires_at = int(timestamp)
                case _:
                    return ErrorString(f"ERR Unsupported option: {option_name}")
            key_store.set(key, value, expires_at=expires_at)
            return SimpleString("OK")
        case ("GET", [key]):
            value = key_store.get(key)
            if value is None:
                return NilBulkString()
            else:
                return BulkString(value)
        case _:
            return ErrorString(f"ERR Unsupported command: {command}")


def execute_request(query: io.TextIOBase) -> bytes:
    request = parse_resp_value(query)
    print("request", request)
    if not isinstance(request, RESPArray) or not all(isinstance(elem, BulkString) for elem in request):
        raise Exception("Expected array containing bulk strings")
    request = [str(elem) for elem in request]
    result = execute_command(request)
    print(f"command '{' '.join(request) }' result", repr(result))
    return serialize_resp_value(result).encode()


def start_low_level_server():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    [client_connection, _client_address] = server_socket.accept()  # wait for client

    while True:
        # No handling of requests longer than 1024
        query = client_connection.recv(1024).decode()
        if not query:
            break
        # print_prefix_lines(query, "client:")

        while query:
            query_stream = StringIO(query)
            result = execute_request(query_stream)
            client_connection.send(result)
            query = query_stream.read()


class RedisConnectionHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        print("Received connection", self.client_address)
        input = io.TextIOWrapper(self.rfile, newline="\r\n")
        while True:
            try:
                result = execute_request(input)
            except EOFError:
                break
            self.wfile.write(result)
        print("Closed connection", self.client_address)


def start_threaded_server():
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("localhost", 6379), RedisConnectionHandler) as server:
        try:
            server.serve_forever()
        finally:
            server.shutdown()
            server.server_close()


def main():
    start_threaded_server()


if __name__ == "__main__":
    main()
