# FTserver.py
# File Transfer server accepting connections from one client at a time and either
# uploading a file from the client or downloading a file to the client
# CPSC 526 Assignment 4 - Fall 2017
# Authors: Shane Sims and Mason Lieu
# Version: 10 November 2017
# Sources viewed or consulted:
# http://www.binarytides.com/python-socket-server-code-example/ - for help structuring server
# https://www.digitalocean.com/community/tutorials/how-to-handle-plain-text-files-in-python-3 - for information on file creation
from __future__ import print_function                                           # Import python3 print function
import os, random, string, hashlib, sys, socket, io
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def authenticate_client(connection, key):
    global cipher
    global session_key
    global iv

    #Receive first msg=(cipher, client_nonce) from the client "in the clear"
    cipher_nonce = connection.recv(1024)
    cipher_nonce= str(cipher_nonce).split(",")
    cipher = cipher_nonce[0]
    client_nonce = cipher_nonce[1]
    print(" cipher=" + cipher)
    print("nonce=" + client_nonce)

    #Create unique session key and iv
    session_key = getSessionKey(client_nonce)
    iv = getIV(client_nonce)
    print("IV=" + ''.join(x.encode('hex') for x in iv))

    if cipher != "null":
        print("SK=" + ''.join(x.encode('hex') for x in session_key))
    #Send challenge to client and authenticate using their response
    challenge_nonce = os.urandom(16)
    sendData(connection, challenge_nonce)
    client_response = rcvData(connection, 1024)
    test_string = hashlib.sha256(KEY + challenge_nonce).digest()
    if client_response == test_string:
        print("Authentication successful")
        #sendData(connection, ACK)                                               # send authentication succesful ACK
        return True
    else:
        print("Authentication failed.")
        #sendData(connection, ERROR)
        connection.close()
        return False

def serve(connection):
    global fileName

    data = rcvData(connection, 1024)                                            # Receive command from client

    if str(data) == "write":                                                    # Client wants to upload file
        sendData(connection, ACK)
        fileName = rcvData(connection, 1024)                                    # Get name of file to be uploaded
        fileName = (str(fileName)).replace('\n','')                             # for connecting with netcat
        print("Command: write   File name: " + fileName)
        theFile = open(fileName, "w+")                                          # Create file obj with specified name or write over file if already exists in dir
        sendData(connection, fileName.encode())                                 # Echo file name back to client to indicate ready to receive
        while 1:                                                                # Receive file data from client until no more sent
            data = rcvData(connection, 1040)                                    # Receive up to 1040 bytes = 1024 byte message + 16 byte padding
            if len(data) == 0:
                break
            theFile.write(data)                                                 # Write data to file
        theFile.close()                                                         # Close/finish writting to file and
        sendData(connection, ACK)                                               # Send success indicator
        print("Status: Client successfully wrote file")

    elif str(data) == "read":                                                   # Client wants to download file
        sendData(connection, ACK)                                               # Ready to get fileNmame
        fileName = rcvData(connection, 1024)                                    # Get name of file to be sent to client
        fileName = (str(fileName)).replace('\n','')                             # for connecting with netcat
        print("Command: read   File name: " + fileName)
        if os.path.exists(fileName):
            theFile = open(fileName, "r")
            data = theFile.read()
            fileSize = len(data)
            sendData(connection, str(fileSize).encode())                        # Send file size so client knows file exists and will come next
            readyResponse = rcvData(connection, 1024)                           # Will receive 1 when client ready to receive
            if str(readyResponse) == "1":
                theFile.seek(0)                                                 # Reset file pointer to beginning of file
                block = theFile.read(1024)                                      # Read and encrypt 1024 bytes at a time from the file
                while len(block) > 0:
                    sendData(connection, block)
                    block = theFile.read(1024)
                theFile.close()
                status = rcvData(connection, 1024)
                if str(status) == "1":
                    print("Status: Client successfully read file")
                else:
                    print("Status: fail. Client did not receive file.")
            else:
                print("Status: fail. Client not ready")

        else:
            sendData(connection, ERROR)                                         # File DNE, send protocol error code
            print("Status: fail - " + fileName + " does not exist on server")
    else:
        sendData(connection, ERROR)                                             # Invalid argument from client, respond with error code
    connection.close()

# Encrypt (if enabled) and send data bytes
def sendData(conn, data):
    if cipher != "null":
        encrypted_bytes = doEncrypt(data)
        conn.sendall(encrypted_bytes)
    else:
        conn.sendall(data)
    return

# Receive data bytes and decrypt (if enabled)
def rcvData(conn, size):
    data = conn.recv(size)
    if (len(data) > 0) and (cipher != "null"):
        encrypted_bytes = data
        decrypted_bytes = doDecrypt(encrypted_bytes)
        return decrypted_bytes
    return data

# Pads using PKCS7 padding then encrypts
def doEncrypt(plaintext):
    encryptor, padder = initEncryptor()
    padded_bytes = padder.update(plaintext) + padder.finalize()
    encrypted_bytes = encryptor.update(padded_bytes) + encryptor.finalize()
    return encrypted_bytes

# Decrypts then unpads using PKCS7 padding
def doDecrypt(ciphertext):
    # Initialize cipher objects
    decryptor, unpadder = initDecryptor()
    decrypted_bytes = decryptor.update(ciphertext) + decryptor.finalize()
    unpadded_bytes = unpadder.update(decrypted_bytes) + unpadder.finalize()
    return unpadded_bytes

# Create encryptor and padder objects needed for AES-CBC
def initEncryptor():
        backend = default_backend()
        cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=backend)        # Creates Cipher object using AES-CBC encryption
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()                                                # Creates padding objects to pad using PKCS7, the argument determines what multiple the data needs to be in (eg. 128 bit blocks for AES-CBC)
        return encryptor, padder

# Create decryptor and unpadder objects needed for AES-CBC
def initDecryptor():
        backend = default_backend()
        cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=backend)        # Creates Cipher object using AES-CBC encryption
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()
        return decryptor, unpadder

# Create session key using sha3-256(seed|nonce|"SK")
def getSessionKey(nonce):
    session_key = hashlib.sha256(KEY + nonce + "SK").digest()
    if cipher == "aes128":
        return session_key[:16]                                                 # Returns the first 16 bytes for AES-CBC-128
    elif  cipher == "aes256":
        return session_key                                                      # Returns all 32 bytes for AES-CBC-256

# Create IV using sha3-256(seed|nonce|"IV")
def getIV(nonce):
    iv = hashlib.sha256(KEY + nonce + "IV").digest()
    return iv[:16]                                                              # Returns the first 16 bytes (ie. the correct size for an IV in AES-CBC)


def main():
    global PORT
    global KEY
    global ACK
    global READ
    global WRITE
    global ERROR

    if(len(sys.argv) == 3):
        PORT = int(sys.argv[1])
        KEY  = str(sys.argv[2])
        ACK = "1".encode()
        READ = "read".encode()
        WRITE = "write".encode()
        ERROR = "-1".encode()

        # Start listening on PORT
        listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            # create TCP socket to communicate with IPv4 addresses
        #TODO: should we wrap the bind in try/except? why/why not?
        listening_socket.bind(("localhost",PORT))
        listening_socket.listen(5)                                                      # listen for client connections with queue for 5 connections
        print("FTserver started and listening on port " + str(PORT) + "\nUsing secret key: " + str(KEY))
        try:
            while 1: #listen for client connections - serve - repeat
                print("Waiting for client connection...")
                client_connection, client_address = listening_socket.accept()
                sys.stdout.write("New connection from client on address " + str(client_address))
                if authenticate_client(client_connection, KEY) :
                    serve(client_connection)
                else:
                    print("Error: wrong key", file = sys.stderr)
                    print("Current key is: " + KEY)
        except KeyboardInterrupt:
            print("\nControl-C detected. Closing server...")
            listening_socket.close()
            sys.exit(0)
    else:
        print("Error: wrong command line arguments", file = sys.stderr)


if __name__ == "__main__":
  main()
