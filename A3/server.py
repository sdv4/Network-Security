import socket
import sys

HOST, PORT = "localhost", 8888
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
server_socket = socket.socket()
server_socket.bind((HOST, PORT))
server_socket.listen(0)

try:
    while True:
        print("Waiting for client")
        client_socket, info = server_socket.accept()


except Exception as err:
    print("Exception Occured: {}.".format(err))
    pass


server_socket.close()
