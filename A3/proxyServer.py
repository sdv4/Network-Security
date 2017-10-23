import socketserver
import sys
import socket
import datetime

#look at select library - will need to use



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
                data = self.request.recv(self.BUFFER_SIZE)                      # self.request is the TCP socket connected to the client and recv stores command from client into data
                if len(data) == self.BUFFER_SIZE:                               # Client sent string of BUFFER_SIZE
                    while 1:                                                    # Check to see if there is more data in the string
                        try:                                                    # error means no more data
                            data += self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
                        except:
                            break
                if len(data) == 0:
                    break
                #TODO: change from decoding to custom formatting so that we can have ---> prepended to each input line and <--- to output lines
                print(data.decode("utf-8"))
                print("\n\n")
                # Send proxy client data to remote server
                remote_client_socket.sendall(data)

                # Receive remote server response

                #received_from_remote  = remote_client_socket.recv(1024)
                while 1:
                    remote_data = remote_client_socket.recv(1024)
                    if not remote_data:
                        break
                    self.request.sendall(remote_data)
                    print(remote_data.decode("utf-8"))


                #Send remote server response data to proxy client
        finally:
            remote_client_socket.close()



if __name__ == "__main__":
    global destServer
    global destPort
    global HOST

    if(len(sys.argv) < 4):
        print("Usage: python3 proxyServer.py <source port> <server> <destination port>")
    else:
        HOST, srcPort = "localhost", int(sys.argv[1])                           # Get port number to listen on as command line input
        destServer, destPort = str(sys.argv[2]), int(sys.argv[3])               # Get destination server name or IP and port number to connect to
        server = socketserver.TCPServer((HOST, srcPort), proxyServerHandler)    # Instantiate the TCP server class and pass handler for http to it
        print("Port logger running: srcPort=" + str(srcPort) + " host=" + destServer + " dstPort=" + str(destPort))
        server.serve_forever()
