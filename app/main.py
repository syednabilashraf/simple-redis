from io import StringIO
import io
import socket

from app.resp import BulkString, ErrorString, RESPArray, RESPValue, SimpleString, parse_resp_value, serialize_resp_value


def print_prefix_lines(text: str, prefix: str):
    print(*(prefix + line for line in text.splitlines()), sep="\n")


def execute_command(command: str) -> RESPValue:
    if command == "PING":
        return SimpleString("PONG")
    else:
        return ErrorString(f"ERR Unsupported command: {command}")


def execute_request(query: io.TextIOBase) -> bytes:
    request = parse_resp_value(query)
    print("request", request)
    if not isinstance(request, RESPArray):
        raise Exception("Expected array containing user requests")
    all_results = bytes()
    for command in request:
        if not isinstance(command, BulkString):
            raise Exception("Expected string command")
        command = command.upper()
        result = execute_command(command)
        print("command", command, "result", result)
        all_results = all_results + serialize_resp_value(result).encode()
    return all_results


def main():
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


if __name__ == "__main__":
    main()
