# Sources viewed or consulted:
# https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/ - for information on the cryptography package
# https://docs.python.org/2/library/hashlib.html - for information on the standard hash module

import os, random, string, hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

#=======================DEFINITIONS=====================
# The following definitions were my attempt at making this program modular.
# The definitions could easily be put into the "main" function of the program and it will work just the same

# Create session key using sha-256(seed|nonce|"SK")
# Input: String <seed>, String <nonce>, String <key_length>
# Output: String <session_key>
def getSessionKey(seed, nonce, key_length):
    session_key = hashlib.sha256(seed + nonce + "SK").digest()
    if key_length == "128":
        return session_key[:16]                         # Returns the first 16 bytes for AES-CBC-128
    elif  key_length == "256":
        return session_key                              # Returns all 32 bytes for AES-CBC-256

# Create IV using sha-256(seed|nonce|"IV")
# Input: String <seed>, String <nonce>
# Output: String <initialization_vector>
def getIV(seed, nonce):
    iv = hashlib.sha256(seed + nonce + "IV").digest()
    return iv[:16]                                      # Returns the first 16 bytes (ie. the correct size for an IV in AES-CBC)

# Create encryptor, decryptor, padder, and unpadder objects needed for AES-CBC
# Input: String <session_key>, String <initialization_vector>
# Output: Cipher <encryptor>, Cipher <decryptor>, padding <padder>, padding <unpadder>
def initializeCipher(session_key, iv):
        backend = default_backend()                                                         # Note: cryptography.io was originally designed to support multiple backends, but this design has been deprecated. So we will use default_backend()
        cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=backend)        # Creates Cipher object using AES-CBC encryption
        encryptor = cipher.encryptor()
        decryptor = cipher.decryptor()
        padder = padding.PKCS7(128).padder()                                                # Creates padding objects to pad using PKCS7, the argument determines what multiple the data needs to be in (eg. 128 bit blocks for AES-CBC)
        unpadder = padding.PKCS7(128).unpadder()
        return encryptor, decryptor, padder, unpadder

# Verify the client's response to the challenge with the server's own digest
# Input: String <client_response>, bytes <nonce>, String <session_key>
# Output: True if digests are the same, False otherwise
def checkResponse(client_response, nonce, session_key):
    server_response = hashlib.sha256(challenge + session_key).digest()
    if server_response == client_response:
        return True
    else:
        return False

if __name__ == "__main__":

    print("===================================================================")            # Used to separate each execution of the program

    #==========================INITIALIZATION==============================
    # Get desired key length of AES-CBC from user, 128 or 256 bit encryption
    key_length = 0
    while key_length != "128" and key_length != "256":
        key_length = raw_input("Enter what key length AES-CBC-<key_length> to use. 128 or 256: ")

    # Generate nonce, session_key, and iv
    seed = raw_input("Enter your secret key: ")
    nonce = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)) # Concatenates 16 randomly chosen alphanumeric characters
    session_key = getSessionKey(seed, nonce, key_length)
    iv = getIV(seed, nonce)

    # Initialize cipher objects
    encryptor, decryptor, padder, unpadder = initializeCipher(session_key, iv)

    #==========================AUTHENTICATION==============================
    # Challenge response could simply be to compute sha256(challenge|session_key)
    # The challenge will pass if the client's and server's digest are the same (ie. they both have the same session key)

    # To be done by the server: Create 16 byte nonce, then send it to the client
    challenge = os.urandom(16)

    # To be done by the client: compute sha256(challenge|session_key) then send response to server
    client_response = hashlib.sha256(challenge + session_key).digest()

    # To be done by the server: compute sha256(challenge|session_key) then verify own hash with client's response
    if checkResponse(client_response, challenge, session_key):
        print("Client verified!")
    else:
        print("Client could not be verified.")

    print("Secure file transfer using the following" +
            "\nMode: AES-CBC-" + str(len(session_key)*8) +
            "\nSecret key: " + seed +
            "\nSession key: " + session_key +
            "\nIV: " + iv +
            "\nClient nonce: " + nonce +
            "\nChallenge nonce: " + challenge)


    #========================ENCRYPTION OF FILE============================
    # Open file to encrypt and writes to "encrypted"
    while True:                                                                             # To Shane: this while-loop might be a less-than-ideal way to ensure that the user inputs a valid file
        file_name = raw_input("Enter file name you wish to encrypt: ")
        try:
            host_file = open(file_name, 'r')                                                # The original file that needs encrypting
            encrypted_file = open("encrypted", 'w')                                         # The encrypted file that will be sent
        except:
            print("Error: Could not open file " + file_name)
        else:
            break

    # Read file in 1024 byte blocks, and encrypt blocks
    # Output file: encrypted
    block = host_file.read(1024)                                                            # Read from file 1024 bytes at a time
    encrypted_bytes =b''                                                                    # Initialize byte string
    while len(block) > 0:
        if len(block) != 1024:                                                              # True if the last block is less than 1024 bytes (ie. it is possible that it is not a multiple of 16 bytes which is required for AES-CBC)
            padded_block = padder.update(block) + padder.finalize()                         # Pad the last block of bytes read so that it is a multiple of 16 bytes
            encrypted_bytes += encryptor.update(padded_block)                               # Encrypt the padded blocks and add to byte string
        else:
            encrypted_bytes += encryptor.update(block)                                      # Encrypt the blocks and add to byte string
        block = host_file.read(1024)
    host_file.close()
    encrypted_bytes += encryptor.finalize()                                                 # Finalize the encryption and add final blocks to byte string

    # Write encrypted bytes to file
    encrypted_file.write(encrypted_bytes)
    encrypted_file.close()
    print("Encryption successful. Output: encrypted")


    #========================DECRYPTION OF FILE============================
    # Open file to decrypt and writes to "decrypted"
    while True:
        tmp = raw_input("Press enter to start decryption of encrypted file")
        try:
            received_file = open("encrypted", 'r')                                          # The received encrypted file that needs decrypting
            decrypted_file = open("decrypted", 'w')                                         # The received decrypted file
        except:
            print("Error: Could not open file.")
        else:
            break

    # Read file in 1024 byte blocks, and decrypt blocks
    # Very similar to encryption except the unpadding follows after decryption
    # Output file: decrypted
    block = received_file.read(1024)
    decrypted_bytes =b''
    while len(block) > 0:
        decrypted_bytes += decryptor.update(block)
        block = received_file.read(1024)
    received_file.close()
    decrypted_bytes += decryptor.finalize()
    decrypted_bytes = unpadder.update(decrypted_bytes) + unpadder.finalize()                # Unpads the plaintext if padding was needed during encryption

    # Write decrypted bytes to file
    decrypted_file.write(decrypted_bytes)
    decrypted_file.close()
    print("Decryption successful. Output: decrypted")
