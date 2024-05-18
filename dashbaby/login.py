import base64

import requests


def xor_encrypt_decrypt(data: bytes, key: int) -> bytes:
    key_bytes = key.to_bytes(2, byteorder="big")  # Convert the key to two bytes
    key1, key2 = key_bytes[0], key_bytes[1]  # Split the key into two parts

    # Process the data in pairs of bytes
    result = bytearray()
    for i in range(0, len(data), 2):
        byte1 = data[i] ^ key1
        if i + 1 < len(data):
            byte2 = data[i + 1] ^ key2
            result.extend([byte1, byte2])
        else:
            result.extend([byte1])

    return bytes(result)


def check_url(encrypted_url: str, key: int) -> bool:
    decrypted_url = decrypt_url(encrypted_url, key)

    # Make an HTTP request to the decrypted URL
    try:
        response = requests.get(decrypted_url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False


def decrypt_url(encrypted_url: str, key: int) -> str:
    # Decode the base64 encoded encrypted URL
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_url)

    # Decrypt the URL
    decrypted_bytes = xor_encrypt_decrypt(encrypted_bytes, key)
    return decrypted_bytes.decode()


def decrypt_urls(descriptor: dict, key: int) -> dict:
    for spreadsheet_type in ["data_spreadsheet", "meds_spreadsheet"]:
        spreadsheet = descriptor.get(spreadsheet_type, {})
        if spreadsheet.get("is_encrypted", False):
            encrypted_url = spreadsheet.get("url")
            decrypted_url = decrypt_url(encrypted_url, key)
            spreadsheet["url"] = decrypted_url
            spreadsheet["is_encrypted"] = False
    return descriptor
