from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256, HMAC
from Crypto.Protocol.KDF import PBKDF2

def generate_rsa_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def encrypt_message(message, public_key):
    recipient_key = RSA.import_key(public_key)
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    encrypted_message = cipher_rsa.encrypt(message.encode())
    return encrypted_message

def decrypt_message(encrypted_message, private_key):
    key = RSA.import_key(private_key)
    cipher_rsa = PKCS1_OAEP.new(key)
    decrypted_message = cipher_rsa.decrypt(encrypted_message).decode()
    return decrypted_message

def generate_mac(message, secret_key):
    print("Secret Key (bytes) in generate_mac:", secret_key)
    print("Message (bytes) in generate_mac:", message)
    hmac = HMAC.new(secret_key, digestmod=SHA256)
    hmac.update(message)
    mac = hmac.digest()
    print("Generated MAC (hex):", mac.hex())
    return mac

def verify_mac(message, mac, secret_key):
    print("Secret Key (bytes) in verify_mac:", secret_key)
    print("Message (bytes) in verify_mac:", message)
    print("MAC (bytes) in verify_mac:", mac)
    hmac = HMAC.new(secret_key, digestmod=SHA256)
    hmac.update(message)
    try:
        hmac.verify(mac)
        print("MAC verification successful")
        return True
    except ValueError:
        print("MAC verification failed")
        return False

def generate_shared_secret(private_key, public_key):
    shared_key = PBKDF2(private_key, public_key, dkLen=16, count=10000)
    return shared_key