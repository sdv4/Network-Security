# FTclient.py
# Implements custom protocol - to be used with FTserver.py
# File Transfer client for uploading a file to a server or downloading a file from a server
# CPSC 526 Assignment 4 - Fall 2017
# Authors: Shane Sims and Mason Lieu
# Version: 10 November 2017
# Sources viewed or consulted:
# https://docs.python.org/3/library/fileinput.html#fileinput.FileInput - for info on reading from stdin
from __future__ import print_function                                           # Import python3 print function
import os, random, string, hashlib, socket, sys, fileinput, io
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def download(conn):
    sendData(conn, READ)                                                        # Indicate to server that client wants to download files
    data = rcvData(conn, 1024)
    if str(data) == "1":                                                        # Server ready to receive fileName
        sendData(conn, fileName.encode())
        fileSize = rcvData(conn, 1024)                                          # receive file size from
        if str(fileSize) != "-1":
            try:
                sendData(conn, ACK)                                             # Indicate ready to read file from server
                theFile = b''
                while 1:
                    if len(theFile) == int(fileSize):                           # Read up to file size
                        break
                    data = rcvData(conn, 1040)                                  # Receive up to 1040 bytes = 1024 byte message + 16 byte padding
                    theFile += data
                print(theFile)
                sendData(conn, ACK)
            except Exception as e:
                sendData(conn, ERROR)
                print("Error: " + str(e))
        else:
            print("Error: file could not be read by server", file = sys.stderr)
    else:
        print("Error: file could not be read by server", file = sys.stderr)
    conn.close()
    sys.exit()

def upload(conn):
    sendData(conn, WRITE)                                                       # Indicate to server that client wants to upload files
    data = rcvData(conn, 1024)
    if str(data) == "1":
        sendData(conn, fileName.encode())                                       # Send file name to server to start transfer
        fileNameEcho = rcvData(conn, 1024)
        if str(fileNameEcho) == fileName :
            print(fileName)
            block = b''
            for line in fileinput.input(files='-',):
                block += line                                                   # 'Block' is treated as a queue of bytes from 'line' and 1024 bytes exit at a time
                if len(block) >= 1024:
                    full_block = block[:1024]                                   # Cut the first 1024 bytes from block to encrypt and send
                    block = block[1024:len(block)]                              # Keep the remainder of the block
                    sendData(conn, full_block)
            sendData(conn, block)                                               # Encrypt then send the remainder of block
            conn.shutdown(socket.SHUT_WR)
            statusResponse = rcvData(conn, 1024)
            if str(statusResponse) == "1":
                print("Upload successful - closing client...")
        else:
            print("Error: file could not be written by server", file = sys.stderr)
    else:
        print("Error: file could not be written by server", file = sys.stderr)
    conn.close()
    sys.exit()

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
    global HOST
    global command
    global fileName
    global cipher
    global session_key
    global iv
    global ACK
    global READ
    global WRITE
    global ERROR

    if(len(sys.argv) == 6):
        command = str(sys.argv[1])
        fileName = str(sys.argv[2])
        hostPort = ((str(sys.argv[3])).split(':'))
        HOST = hostPort[0]
        PORT = int(hostPort[1])
        cipher = str(sys.argv[4])
        KEY  = str(sys.argv[5])
        ACK = "1".encode()
        READ = "read".encode()
        WRITE = "write".encode()
        ERROR = "-1".encode()

        client_nonce = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)) # Concatenates 16 randomly chosen alphanumeric characters
        # Initialize AES arguments
        session_key = getSessionKey(client_nonce)
        iv = getIV(client_nonce)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((HOST, PORT))

        # Authenticate client to server
        first_msg = cipher + "," + client_nonce
        server_socket.sendall(first_msg)                                        # Sebd cipher,nounce to server
        server_challenge = rcvData(server_socket, 1024)
        challenge_response = hashlib.sha256(KEY + server_challenge).digest()
        sendData(server_socket, challenge_response)


        # Successful Authentication
        if command == "write":
            upload(server_socket)

        elif command == "read":
            download(server_socket)
        else:
            print(command)
            print("Error: wrong command line arguments", file = sys.stderr)

    else:
        print("Error: wrong command line arguments", file = sys.stderr)


if __name__ == "__main__":
  main()
