import os, random, string, hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

#TODO
#Input: bytes <key>, bytes <iv>
#Output: <bytes> object
#def createCipher(key, iv):


#TODO
#Input: <>, <>, <>, <>
#Output: <bytes> object
#def doEncrypt():


#TODO
#Input: <>, <>, <>, <>
#Output: <bytes> object
#def doDecrypt():

#TODO
#Input: <>, <>, <>, <>
#Output: <bytes> object
#def doHash():

#TODO
#def bytes getSessionKey(seed):

def getSessionKey(seed, nonce, mode):
    session_key = hashlib.sha256(seed + nonce + "SK").digest()
    if mode == "128":
        return session_key[:16]
    elif  mode == "256":
        return session_key

def checkResponse(client_response, nonce, session_key):
    server_response = hashlib.sha256(challenge + session_key).digest()
    if server_response == client_response:
        return True
    else:
        return False

if __name__ == "__main__":

    #==========================INITIALIZATION==============================
    #Get security mode of AES-CBC from user, 128 or 256 bit encryption
    mode = 0
    while mode != "128" and mode != "256":
        try:
            mode = raw_input("Enter what AES-CBC-<bit> mode to use. Either '128' or '256': ")
        except NameError:
            print("\nError: Please enter either '128' or '256'")

    #Create session key using sha-256(seed|nonce|"SK")
    seed = raw_input("Enter a seed to create key: ")
    nonce = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
    session_key = getSessionKey(seed, nonce, mode)
    print("Using key size: " + str(len(session_key)))

    #Create IV using sha-256(seed|nonce|"IV")
    IV = hashlib.sha256(seed + nonce + "IV").digest()
    IV = IV[:16]

    #Create encryptor, decryptor, and padder
    #Note: cryptography.io was originally designed to support multiple backends, but this design has been deprecated. So we will use default_backend()
    backend = default_backend()
    cipher = Cipher(algorithms.AES(session_key), modes.CBC(IV), backend=backend)
    encryptor = cipher.encryptor()
    decryptor = cipher.decryptor()
    padder = padding.PKCS7(128).padder()
    unpadder = padding.PKCS7(128).unpadder()

    #==========================AUTHENTICATION==============================
    #Challenge response could simply be to compute sha256(challenge|session_key)
    challenge = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
    client_response = hashlib.sha256(challenge + session_key).digest()
    if checkResponse(client_response, challenge, session_key):
        print("Client verified!")
    else:
        print("Client could not be verified.")

    #==========================ENCRYPTION OF FILE==============================
    #Open file to encrypt and writes to "encrypted"
    while True:
        file_name = raw_input("Enter file name you wish to encrypt: ")
        try:
            host_file = open(file_name, 'r')
            encrypted_file = open("encrypted", 'w')
        except:
            print("Could not open file.")
        else:
            break

    #Read file in 1024 byte blocks, encrypt blocks
    block = host_file.read(1024)
    encrypted_bytes =b''
    while len(block) > 0:
        if len(block) != 1024:
            padded_block = padder.update(block)
            padded_block += padder.finalize()
            encrypted_bytes += encryptor.update(padded_block)
        else:
            encrypted_bytes += encryptor.update(block)
        block = host_file.read(1024)
    encrypted_bytes += encryptor.finalize()
    host_file.close()

    #Write encrypted bytes to file
    encrypted_file.write(encrypted_bytes)
    encrypted_file.close()

    #==========================DECRYPTION OF FILE==============================
    #Open file to decrypt and writes to "decrypted"
    while True:
        file_name = raw_input("Enter file name you wish to decrypt: ")
        try:
            received_file = open(file_name, 'r')
            decrypted_file = open("decrypted", 'w')
        except:
            print("Could not open file.")
        else:
            break

    #Read file in 1024 bit (128 byte) blocks, decrypt blocks
    block = received_file.read(1024)
    decrypted_bytes =b''
    while len(block) > 0:
        decrypted_bytes += decryptor.update(block)
        block = received_file.read(1024)
    decrypted_bytes += decryptor.finalize()
    decrypted_bytes = unpadder.update(decrypted_bytes) + unpadder.finalize()
    received_file.close()

    #Write decrypted bytes to file
    decrypted_file.write(decrypted_bytes)
    decrypted_file.close()
















    #Create 16-byte nonce
