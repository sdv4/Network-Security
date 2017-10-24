import socketserver
import sys
import socket
import datetime


#TODO: provide some file documentation at top
#TODO: add support for more than one connections: look at select library - will need to use
#TODO: implement all forms of the logging options
#TODO: add ability to close program on keyboard interupt, so not spilling error codes to stdout


# Handler for proxy to remote server
class proxyServerHandler(socketserver.BaseRequestHandler):

    BUFFER_SIZE = 1024

    def handle(self):

        try:
            # Connect to remote server on specified port
            remote_client_socket = socket.socket()
            remote_client_socket.connect((destServer, destPort))
            currentDateTime = datetime.datetime.now()
            print("New connection: " + str(currentDateTime) + ", from " + str(HOST) + "\n" )
            while 1:
                # Get proxy client data in variable 'data'
                data = self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)                      # self.request is the TCP socket connected to the client and recv stores command from client into data
                if len(data) == self.BUFFER_SIZE:                               # Client sent string of BUFFER_SIZE
                    while 1:                                                    # Check to see if there is more data in the string
                        try:                                                    # error means no more data
                            data += self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
                        except:
                            break
                if len(data) == 0:
                    break

                # Print data recieved from proxy client to standard ourput before sending to remote server
                data_lines = data.split(b'\n')                                  # Split raw data into lines
                for line in data_lines:
                    print("---> " + str(line))                       # Print each line with arrow
                print("\n\n")

                # Send proxy client data to remote server
                remote_client_socket.sendall(data)

                # Receive remote server response and print each line formatted to std output
                # then send remote server response data to proxy client

                while 1:
                    remote_data = remote_client_socket.recv(1024)
                    if not remote_data:
                        break
                    self.request.sendall(remote_data)
                    data_lines = remote_data.split(b'\n')                       # Split raw data into lines
                    for line in data_lines:
                        print("<--- " + str(line))                   # Print each line with arrow


        finally:
            remote_client_socket.close()
            print("Connection closed.")



if __name__ == "__main__":
    global destServer
    global destPort
    global HOST
    global loggingOption
    global replaceOptions

    # Optional arg(s) given, determine how many and set flag(s)
    if len(sys.argv) >= 4:

        #Two optional arguments given.
        if len(sys.argv) == 6:
            loggingOption = str(sys.argv[1])
            replaceOptions = str(sys.argv[2])
            HOST, srcPort = "localhost", int(sys.argv[3])                           # Get port number to listen on as command line input
            destServer, destPort = str(sys.argv[4]), int(sys.argv[5])               # Get destination server name or IP and port number to connect to
            server = socketserver.TCPServer((HOST, srcPort), proxyServerHandler)    # Instantiate the TCP server class and pass handler for http to it

        # One optional argument given. Check that they are in correct order or pass to else and TODO: check which one is set, has to be format?
        elif len(sys.argv) == 5:
            loggingOption = str(sys.argv[1])
            HOST, srcPort = "localhost", int(sys.argv[2])                           # Get port number to listen on as command line input
            destServer, destPort = str(sys.argv[3]), int(sys.argv[4])               # Get destination server name or IP and port number to connect to
            server = socketserver.TCPServer((HOST, srcPort), proxyServerHandler)    # Instantiate the TCP server class and pass handler for http to it

        # No optional command line arguments given
        else:
            loggingOption = "none"
            HOST, srcPort = "localhost", int(sys.argv[1])                           # Get port number to listen on as command line input
            destServer, destPort = str(sys.argv[2]), int(sys.argv[3])               # Get destination server name or IP and port number to connect to
            server = socketserver.TCPServer((HOST, srcPort), proxyServerHandler)    # Instantiate the TCP server class and pass handler for http to it

        print("Port logger running: srcPort=" + str(srcPort) + " host=" + destServer + " dstPort=" + str(destPort))
        server.serve_forever()

    else:
        print("Usage: python3 proxyServer.py [logOptions] [replaceOptions]" +
                "<source port> <server> <destination port>")
