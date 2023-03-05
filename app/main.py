import socket


def print_prefix_lines(text: str, prefix: str):
    print(*(prefix + line for line in text.splitlines()), sep="\n")


def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    [client_connection, client_address] = server_socket.accept()  # wait for client

    while True:
        # No handling of requests longer than 1024
        query: str = client_connection.recv(1024).decode()
        if not query:
            break
        print_prefix_lines(query, "client:")
        client_connection.send(b"+PONG\r\n")


if __name__ == "__main__":
    main()
