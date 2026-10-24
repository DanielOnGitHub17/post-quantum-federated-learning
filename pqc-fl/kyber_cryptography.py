import base64
import hashlib
import logging
import time

from kyber_py.ml_kem import ML_KEM_512

logger = logging.getLogger(__name__)

_KEM_CIPHERTEXT_SIZE = 32 * (ML_KEM_512.du * ML_KEM_512.k + ML_KEM_512.dv)


def generate_key_pair() -> tuple[bytes, bytes]:
    """Generate a fresh ML-KEM-512 public/private key pair."""
    return ML_KEM_512.keygen()


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


def decrypt(
    cipher_text: str,
    private_key: bytes,
    *,
    company_name: str = "unknown",
) -> bytes:
    """Decrypt a Base64 ciphertext and return the original bytes."""
    if not isinstance(cipher_text, str):
        raise TypeError("cipher_text must be a string")

    start_time = time.perf_counter()
    encrypted = base64.b64decode(cipher_text.encode("ascii"), validate=True)
    kem_ciphertext = encrypted[:_KEM_CIPHERTEXT_SIZE]
    encrypted_text = encrypted[_KEM_CIPHERTEXT_SIZE:]
    shared_key = ML_KEM_512.decaps(private_key, kem_ciphertext)
    plain_text = _xor_with_keystream(encrypted_text, shared_key)
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
    return plain_text
