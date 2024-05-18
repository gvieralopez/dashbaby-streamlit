import base64


def xor_encrypt_decrypt(data, key):
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


# URL to encrypt
url = "https://example.com"
url_bytes = url.encode()

# Key for encryption/decryption (must fit within two bytes, e.g., 0-65535)
key = 1234  # Example key

# Encrypt the URL
encrypted_bytes = xor_encrypt_decrypt(url_bytes, key)

# Encode the encrypted bytes to a base64 string for safe storage
encrypted_url = base64.urlsafe_b64encode(encrypted_bytes).decode()

print(f"Encrypted URL: {encrypted_url}")
