from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
from PIL import Image
import base64
import os

# Generate AES-256 key from password
def generate_key(password: str, salt: bytes = None) -> bytes:
    if not salt:
        salt = os.urandom(16)  # Random salt for key derivation
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode()), salt

# Encrypt message using AES-256
def encrypt_message(message: str, key: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return cipher.iv + ciphertext

# Decrypt message using AES-256
def decrypt_message(ciphertext: bytes, key: bytes) -> str:
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    padded_data = decryptor.update(actual_ciphertext) + decryptor.finalize()
    return unpadder.update(padded_data) + unpadder.finalize()

# Encode message into image
def encode_message_in_image(image_path: str, message: bytes, output_path: str):
    with Image.open(image_path) as img:
        encoded_img = img.copy()
        pixels = encoded_img.load()

        # Embed data in the least significant bits of the image pixels
        binary_data = ''.join(format(byte, '08b') for byte in message)
        data_index = 0
        for y in range(encoded_img.height):
            for x in range(encoded_img.width):
                if data_index < len(binary_data):
                    r, g, b = pixels[x, y]
                    r = (r & ~1) | int(binary_data[data_index])
                    pixels[x, y] = (r, g, b)
                    data_index += 1
        encoded_img.save(output_path)

# Decode message from image
def decode_message_from_image(image_path: str) -> bytes:
    with Image.open(image_path) as img:
        pixels = img.load()
        binary_data = ""
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = pixels[x, y]
                binary_data += str(r & 1)

        # Convert binary data to bytes
        byte_data = bytearray()
        for i in range(0, len(binary_data), 8):
            byte_data.append(int(binary_data[i:i+8], 2))
        return bytes(byte_data)
