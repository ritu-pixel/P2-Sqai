import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def get_user_fernet_key(username: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"",
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(username.encode()))


def encrypt_bytes(data: bytes, fernet_key: bytes) -> bytes:
    fernet = Fernet(fernet_key)
    return fernet.encrypt(data)

def decrypt_bytes(token: bytes, fernet_key: bytes) -> bytes:
    fernet = Fernet(fernet_key)
    return fernet.decrypt(token)
