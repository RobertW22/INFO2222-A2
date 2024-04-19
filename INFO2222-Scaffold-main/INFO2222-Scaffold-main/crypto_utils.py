from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
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
    hash_obj = SHA256.new(message)
    signature = pkcs1_15.new(RSA.import_key(secret_key)).sign(hash_obj)
    return signature

def verify_mac(message, signature, secret_key):
    if isinstance(secret_key, bytes):
        secret_key = secret_key.decode()
    
    if not isinstance(secret_key, str):
        raise ValueError("Secret key must be a string")
    
    hash_obj = SHA256.new(message)
    try:
        pkcs1_15.new(RSA.import_key(secret_key)).verify(hash_obj, signature)
        return True
    except (ValueError, TypeError):
        return False

def generate_shared_secret(private_key, public_key):
    shared_key = PBKDF2(private_key, public_key, dkLen=16, count=10000)
    return shared_key