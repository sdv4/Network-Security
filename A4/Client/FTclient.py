# FTclient.py
# Implements custom protocol - to be used with FTserver.py
# File Transfer client for uploading a file to a server or downloading a file from a server
# CPSC 526 Assignment 4 - Fall 2017
# Authors: Shane Sims and Mason Lieu
# Version: 10 November 2017
# Sources viewed or consulted:
# https://docs.python.org/3/library/fileinput.html#fileinput.FileInput - for info on reading from stdin
from __future__ import print_function                                           # Import python3 print function
import os, random, string, hashlib, socket, sys, fileinput
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def download(conn):
    encrypted_bytes = doEncrypt(READ)
    conn.sendall(encrypted_bytes)                                                           # Indicate to server that client wants to download files
    data = conn.recv(1024)
    if str(data) == "1":                                                        # Server ready to receive fileName
        conn.sendall(fileName)
        fileSize = conn.recv(1024)                                              # receive file size from server
        if str(fileSize) != "-1":
            try:
                conn.sendall("1")                                               # Indicate ready to read file from server
                theFile = conn.recv(int(fileSize))                                      # get entire file
                print(theFile)
                conn.sendall("1")
            except:
                conn.sendall("-1")
        else:
            print("Error: file could not be read by server", file = sys.stderr)
    else:
        print("Error: file could not be read by server", file = sys.stderr)
    conn.close()
    sys.exit()

def upload(conn):
    conn.sendall("write")                                                           # Indicate to server that client wants to upload files
    data = conn.recv(1024)
    if str(data) == "0":
        conn.sendall(fileName)
        fileNameEcho = conn.recv(1024)
        if str(fileNameEcho) == fileName :
            print(fileName)
            for block in fileinput.input(files='-',):
                conn.sendall(block)
            conn.shutdown(socket.SHUT_WR)
            statusResponse = conn.recv(1024)
            if str(statusResponse) == "1":
                print("Upload successful - closing client...")
        else:
            print("Error: file could not be written by server", file = sys.stderr)
    else:
        print("Error: file could not be written by server", file = sys.stderr)
    conn.close()
    sys.exit()

# Create session key using sha3-256(seed|nonce|"SK")
def getSessionKey(nonce):
    session_key = hashlib.sha256(KEY + nonce + "SK").digest()
    if cipher == "aes128":
        return session_key[:16]                     # Returns the first 16 bytes for AES-CBC-128
    elif  cipher == "aes256":
        return session_key                         # Returns all 32 bytes for AES-CBC-256

# Create IV using sha3-256(seed|nonce|"IV")
def getIV(nonce):
    iv = hashlib.sha256(KEY + nonce + "IV").digest()
    return iv[:16]              # Returns the first 16 bytes (ie. the correct size for an IV in AES-CBC)

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

def doEncrypt(plaintext):
    # Initialize cipher objects
    encryptor, padder = initEncryptor()
    padded_bytes = padder.update(plaintext) + padder.finalize()
    encrypted_bytes = encryptor.update(padded_bytes) + encryptor.finalize()
    return encrypted_bytes

def doDecrypt(ciphertext):
    # Initialize cipher objects
    decryptor, unpadder = initDecryptor()
    decrypted_bytes = decryptor.update(ciphertext) + decryptor.finalize()
    unpadded_bytes = unpadder.update(decrypted_bytes) + unpadder.finalize()
    return unpadded_bytes

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
        ACK = "1"
        READ = "read"
        WRITE = "write"
        ERROR = "-1"

        client_nonce = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)) # Concatenates 16 randomly chosen alphanumeric characters
        if cipher != "null":
            # Initialize AES arguments
            session_key = getSessionKey(client_nonce)
            iv = getIV(client_nonce)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((HOST, PORT))

        # Authenticate client to server
        first_msg = cipher + "," + client_nonce
        server_socket.sendall(first_msg)                                        # Sebd cipher,nounce to server
        server_challenge = server_socket.recv(1024)
        challenge_response = hashlib.sha256(KEY + server_challenge).digest()
        server_socket.sendall(challenge_response)


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
