import hashlib
import io

import pytest

import app as app_module

app = app_module.app
falcon = app_module.falcon

BINARY = b"\x7fELF example application"


@pytest.fixture(scope="module")
def keys():
    return falcon.keygen()


@pytest.fixture
def client(keys, monkeypatch, tmp_path):
    sk, vk = keys
    digest = hashlib.sha256(BINARY).digest()
    artifact_prefix = tmp_path / "StockPredictor"
    artifact_prefix.with_suffix(".sha256").write_text(digest.hex(), encoding="ascii")
    artifact_prefix.with_suffix(".sig").write_bytes(falcon.sign(sk, digest))
    artifact_prefix.with_suffix(".pub").write_bytes(vk)
    monkeypatch.setattr(app_module, "ARTIFACT_PREFIX", artifact_prefix)
    return app.test_client()


def upload(client, data):
    return client.post("/", data={"binary": (io.BytesIO(data), "app.bin")}, content_type="multipart/form-data").get_data(as_text=True)


def test_matching_binary_passes(client):
    assert "Safe to use" in upload(client, BINARY)


def test_modified_binary_fails_hash(client):
    assert "does not match" in upload(client, BINARY + b"!")


def test_invalid_signature_fails(client, keys, monkeypatch):
    other = falcon.sign(keys[0], b"something else")
    app_module.ARTIFACT_PREFIX.with_suffix(".sig").write_bytes(other)
    assert "Signature is not valid" in upload(client, BINARY)


def test_empty_upload_fails(client):
    assert "No file received" in upload(client, b"")


def test_missing_artifact_fails_safely(client):
    app_module.ARTIFACT_PREFIX.with_suffix(".pub").unlink()
    assert "not set up" in upload(client, BINARY)
