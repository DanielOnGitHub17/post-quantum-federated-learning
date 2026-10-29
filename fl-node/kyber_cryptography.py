import base64
import hashlib
import time

from kyber_py.ml_kem import ML_KEM_512

def _xor_with_keystream(data: bytes, shared_key: bytes) -> bytes:
    encrypted = bytearray()
    counter = 0

    while len(encrypted) < len(data):
        stream_block = hashlib.sha3_256(
            shared_key + counter.to_bytes(4, "big")
        ).digest()
        start = len(encrypted)
        block = data[start : start + len(stream_block)]
        encrypted.extend(
            value ^ stream_block[index] for index, value in enumerate(block)
        )
        counter += 1

    return bytes(encrypted)


def encrypt(plain_bytes: bytes, public_key: bytes) -> str:
    """Encrypt model bytes and return a Base64 string."""
    if not isinstance(plain_bytes, bytes):
        raise TypeError("plain_bytes must be bytes")

    start_time = time.perf_counter()
    shared_key, kem_ciphertext = ML_KEM_512.encaps(public_key)
    encrypted_text = _xor_with_keystream(plain_bytes, shared_key)
    cipher_text = base64.b64encode(kem_ciphertext + encrypted_text).decode("ascii")
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    print(
        "Encrypt: "
        f"public key={len(public_key)} bytes, "
        f"data={len(plain_bytes)} bytes, "
        f"output={len(cipher_text)} characters, "
        f"time={elapsed_ms:.3f} ms"
    )
    return cipher_text
