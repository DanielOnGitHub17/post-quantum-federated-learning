import hashlib
import io

import pytest

from app import app, falcon

BINARY = b"\x7fELF example application"


@pytest.fixture(scope="module")
def keys():
    return falcon.keygen()


@pytest.fixture
def client(keys, monkeypatch):
    sk, vk = keys
    digest = hashlib.sha256(BINARY).digest()
    monkeypatch.setenv("APPLICATION_HASH", digest.hex())
    monkeypatch.setenv("APPLICATION_SIGNATURE", falcon.sign(sk, digest).hex())
    monkeypatch.setenv("FALCON_VERIFICATION_KEY", vk.hex())
    return app.test_client()


def upload(client, data):
    return client.post("/", data={"binary": (io.BytesIO(data), "app.bin")}, content_type="multipart/form-data").get_data(as_text=True)


def test_matching_binary_passes(client):
    assert "Safe to use" in upload(client, BINARY)


def test_modified_binary_fails_hash(client):
    assert "does not match" in upload(client, BINARY + b"!")


def test_invalid_signature_fails(client, keys, monkeypatch):
    other = falcon.sign(keys[0], b"something else")
    monkeypatch.setenv("APPLICATION_SIGNATURE", other.hex())
    assert "Signature is not valid" in upload(client, BINARY)


def test_empty_upload_fails(client):
    assert "No file received" in upload(client, b"")


def test_missing_env_fails_safely(client, monkeypatch):
    monkeypatch.delenv("FALCON_VERIFICATION_KEY")
    assert "not set up" in upload(client, BINARY)
