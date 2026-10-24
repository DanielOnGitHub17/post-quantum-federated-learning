import base64
import hashlib
import logging
import time

from kyber_py.ml_kem import ML_KEM_512

logger = logging.getLogger(__name__)

_PUBLIC_KEY, _PRIVATE_KEY = ML_KEM_512.keygen()
_KEM_CIPHERTEXT_SIZE = 32 * (ML_KEM_512.du * ML_KEM_512.k + ML_KEM_512.dv)


def key_material() -> dict[str, str | int]:
    """Return demo key material in a JSON-safe representation."""
    return {
        "public_key": base64.b64encode(_PUBLIC_KEY).decode("ascii"),
        "private_key": base64.b64encode(_PRIVATE_KEY).decode("ascii"),
        "public_key_length": len(_PUBLIC_KEY),
        "private_key_length": len(_PRIVATE_KEY),
    }


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


def encrypt(plain_text: str, public_key: bytes = _PUBLIC_KEY) -> str:
    """Encrypt arbitrary text and return a Base64 string."""
    if not isinstance(plain_text, str):
        raise TypeError("plain_text must be a string")

    plain_bytes = plain_text.encode("utf-8")
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


def decrypt(
    cipher_text: str,
    private_key: bytes = _PRIVATE_KEY,
    *,
    company_name: str = "unknown",
) -> str:
    """Decrypt a Base64 string and return the original text."""
    if not isinstance(cipher_text, str):
        raise TypeError("cipher_text must be a string")

    start_time = time.perf_counter()
    encrypted = base64.b64decode(cipher_text.encode("ascii"), validate=True)
    kem_ciphertext = encrypted[:_KEM_CIPHERTEXT_SIZE]
    encrypted_text = encrypted[_KEM_CIPHERTEXT_SIZE:]
    shared_key = ML_KEM_512.decaps(private_key, kem_ciphertext)
    plain_text = _xor_with_keystream(encrypted_text, shared_key)
    decrypted_text = plain_text.decode("utf-8")
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "Decrypted result for company=%s: private_key_bytes=%d "
        "ciphertext_bytes=%d plaintext_bytes=%d duration_ms=%.3f",
        company_name,
        len(private_key),
        len(encrypted),
        len(plain_text),
        elapsed_ms,
    )
    return decrypted_text


if __name__ == "__main__":
    print(f"Public key length: {len(_PUBLIC_KEY)} bytes")
    print(f"Private key length: {len(_PRIVATE_KEY)} bytes")
    text = input("Text to encrypt: ")
    encrypted = encrypt(text)
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypt(encrypted)}")
