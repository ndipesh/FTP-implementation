#############
# python3 ftp_tcpserver.py
# usage: python3 ftp_tcpserver.py <7684>
#############

import socket
import sys
import os

BUFFER_SIZE = 512
EOF_MSG = "**EOF**"

if (len(sys.argv) < 2):
    print('usage: python3 ftp_tcpserver.py <Port number>')
    sys.exit()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
server_address = ('0.0.0.0', int(sys.argv[1]))
print('starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)

hostname = socket.gethostname()
server_ip = socket.gethostbyname(hostname)
server_port = sock.getsockname()[1]

print(f"Server is running on IP: {server_ip}")
print(f"Server is listening on port: {server_port}")
print("FTP server running...")

# Listen for incoming connections
sock.listen(5)

while True:
    # Wait for a connection
    print('waiting for a connection', file=sys.stderr)
    connection, client_address = sock.accept()

    try:
        print(f"Accept...")
        print('connection from', client_address, file=sys.stderr)

        # Keep receiving from this client
        while True:
            data = connection.recv(BUFFER_SIZE)
            if not data:
                break

            message = data.decode('utf-8').strip()
            print(f"server received {len(data)} bytes: {message}")

            # --- Menu 1: Check if file exists ---
            if message.startswith('*1:'):
                filename = message[3:]
                print(f"Client {client_address[0]} requests a file name [{filename}]")

                if os.path.isfile(filename):
                    response = f"*1:{filename}:yes"
                    print(f"Server has it and send [{response}] to the client")
                else:
                    response = f"*1:{filename}:no"
                    print(f"Server does not have {filename} and send [{response}] to the client")

                connection.send(response.encode('utf-8'))

            # --- Menu 2: Download a file ---
            elif message.startswith('*2:'):
                filename = message[3:]
                print(f"Client {client_address[0]} requested [{filename}] file to download")

                if os.path.isfile(filename):
                    print(f"Server is sending [{filename}]")
                    with open(filename, 'rb') as f:
                        while True:
                            chunk = f.read(BUFFER_SIZE)
                            if not chunk:
                                break
                            connection.send(chunk)
                    # Send EOF marker
                    print("Server is sending EOF")
                    connection.send(EOF_MSG.encode('utf-8'))
                else:
                    # File not found — notify client
                    response = f"*2:{filename}:no"
                    connection.send(response.encode('utf-8'))
                    print(f"Server does not have [{filename}]")

            # --- Exit ---
            elif message == '0':
                print(f"Client {client_address[0]} disconnected.")
                break

            else:
                print(f"Unknown command: {message}")
                connection.send(b"Unknown command")

    finally:
        # Clean up the connection
        connection.close()
