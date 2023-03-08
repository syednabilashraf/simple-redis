import socket

def send_request(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 6379))
        s.sendall(command.encode())
        response = s.recv(1024)
    return response.decode()

# PING
response = send_request("*1\r\n$4\r\nPING\r\n")
print("PING Response:", response)

# SET
response = send_request("*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n")
print("SET Response:", response)

# GET
response = send_request("*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n")
print("GET Response:", response)

# ECHO
response = send_request("*2\r\n$4\r\nECHO\r\n$5\r\nhello\r\n")
print("ECHO Response:", response)
