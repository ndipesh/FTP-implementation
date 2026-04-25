###############
# python3 ftp_tcpclient.py
# usage: python3 ftp_tcpclient.py <147.97.156.106> <7684>
##############

import socket
import sys
import os

BUFFER_SIZE = 512
EOF_MSG = "**EOF**"

menu = """
===Please enter the menu===
1. Check a file (Usage: *1:filename)
2. Download a file (Usage: *2:filename)
0. Exit (Usage: 0)
"""

if (len(sys.argv) < 3):
    print('usage: python3 ftp_tcpclient.py <IP address> <Port number>')
    sys.exit()

# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (sys.argv[1], int(sys.argv[2]))
print('connecting to %s port %s' % server_address, file=sys.stderr)
sock.connect(server_address)

client_ip, client_port = sock.getsockname()
print(f"Client IP: {client_ip}")
print(f"Client Port: {client_port}")


def get_safe_filename(filename):
    """
    If 'filename' already exists in the current directory,
    append '2' before the extension repeatedly until a free name is found.
    e.g., data.txt -> data2.txt -> data22.txt
    """
    if not os.path.exists(filename):
        return filename

    # Split name and extension
    base, ext = os.path.splitext(filename)
    new_name = base + "2" + ext

    # Keep appending '2' until we find a free name
    while os.path.exists(new_name):
        base2, ext2 = os.path.splitext(new_name)
        new_name = base2 + "2" + ext2

    return new_name


try:
    # Keep running until user enters 0
    while True:
        print(menu)
        userinput = input("Please enter: ").strip()

        if not userinput:
            continue

        # --- Exit ---
        if userinput == '0':
            sock.send('0'.encode('utf-8'))
            print("Exiting. Goodbye!")
            break

        # --- Menu 1: Check if file exists on server ---
        elif userinput.startswith('*1:'):
            filename = userinput[3:]
            if not filename:
                print("Please provide a filename. e.g., *1:data.txt")
                continue

            sock.send(userinput.encode('utf-8'))
            response = sock.recv(BUFFER_SIZE).decode('utf-8')
            print(f"Reply from Server: {response}", file=sys.stderr)

        # --- Menu 2: Download a file from server ---
        elif userinput.startswith('*2:'):
            filename = userinput[3:]
            if not filename:
                print("Please provide a filename. e.g., *2:data.txt")
                continue

            # Determine safe local filename before sending request
            save_filename = get_safe_filename(filename)
            if save_filename != filename:
                print(f"File '{filename}' already exists locally. Saving as '{save_filename}'")

            # Open local file for writing BEFORE sending request
            with open(save_filename, 'wb') as f:
                sock.send(userinput.encode('utf-8'))

                # Receive file contents until EOF marker
                buffer_str = ""
                while True:
                    data = sock.recv(BUFFER_SIZE)
                    if not data:
                        break

                    # Check for EOF (could be mixed with file data or standalone)
                    chunk = data.decode('utf-8', errors='replace')

                    if EOF_MSG in chunk:
                        # Write everything before EOF
                        before_eof = chunk[:chunk.index(EOF_MSG)]
                        if before_eof:
                            f.write(before_eof.encode('utf-8'))
                        print("Received EOF from server. File transfer complete.")
                        break

                    # Check for error response (*2:filename:no)
                    if chunk.startswith('*2:') and chunk.endswith(':no'):
                        print(f"Server does not have the file: {filename}")
                        # Remove the empty file we created
                        f.close()
                        os.remove(save_filename)
                        break

                    f.write(data)

            if os.path.exists(save_filename) and os.path.getsize(save_filename) > 0:
                print(f"File saved as '{save_filename}'")
            elif os.path.exists(save_filename) and os.path.getsize(save_filename) == 0:
                os.remove(save_filename)

        else:
            print("Invalid input. Please use *1:filename, *2:filename, or 0 to exit.")

finally:
    print('closing socket', file=sys.stderr)
    sock.close()
