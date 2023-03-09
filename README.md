# simple-redis
Its a simple Redis server implemented using the Redis serialization protocol (RESP)

## Prerequisite
- python 3.10 or up

## Running the server
Execute the shell script spawn_redis_server.sh. It will run in port 6379.

```bash spawn_redis_server.sh```
## Testing the server
After running the server:
```python3 app/test.py```

## Supported RESP commands:

1) **SET** for storing a key-value pair
Example request: "*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"

3) **GET** for getting value of a key

Example request: "*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n"

4) **PING**

Example request: "*1\r\n$4\r\nPING\r\n"

5) **ECHO**

Example request: "*2\r\n$4\r\nECHO\r\n$5\r\nhello\r\n"

## Example request in python
```
import socket

def send_request(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 6379))
        s.sendall(command.encode())
        response = s.recv(1024)
    return response.decode()

# PING Command
response = send_request("*1\r\n$4\r\nPING\r\n")
print("PING Response:", response) // PING Response: +PONG

# SET Command
response = send_request("*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n")
print("SET Response:", response) // SET Response: +OK

# GET Command
response = send_request("*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n")
print("GET Response:", response) // GET Response: $3\r\nbar

# ECHO Command
response = send_request("*2\r\n$4\r\nECHO\r\n$5\r\nhello\r\n")
print("ECHO Response:", response)

```

## Example request in node
```
const net = require("net");

function sendRedisCommand(command) {
  const client = net.createConnection({ port: 6379, host: "localhost" });
  client.write(command);

  client.on("data", (data) => {
    console.log(data.toString());
    client.end();
  });
}

// PING Command
sendRedisCommand("*1\r\n$4\r\nPING\r\n");

// SET Command
sendRedisCommand("*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n");

// GET Command
sendRedisCommand("*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n");

// ECHO Command
sendRedisCommand("*2\r\n$4\r\nECHO\r\n$5\r\nhello\r\n");

```
