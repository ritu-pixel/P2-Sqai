import os
import uuid
from auth.encryption import decrypt_bytes, get_user_fernet_key

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)
MIME_EXTENSION_MAP = {
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/x-m4a": ".m4a",
}

def decrypt_to_temp_path(encrypted_path: str, current_user: str, content_type: str) -> str:
    ext = MIME_EXTENSION_MAP.get(content_type, ".mp3")  # default fallback

    with open(encrypted_path, "rb") as f:
        encrypted = f.read()

    decrypted = decrypt_bytes(encrypted, get_user_fernet_key(current_user))

    temp_file_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}{ext}")
    with open(temp_file_path, "wb") as f:
        f.write(decrypted)

    return temp_file_path