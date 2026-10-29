"""Flask app that verifies an uploaded binary against its SHA-256 hash and Falcon-512 signature."""
import hashlib
import hmac
import os

from flask import Flask, render_template, request

from falcon import Falcon

app = Flask(__name__)
falcon = Falcon(512)


def check(upload):
    """Return (ok, message, next_step) for the uploaded file; the file is only hashed, never run."""
    try:
        expected_hash = bytes.fromhex(os.environ["APPLICATION_HASH"])
        signature = bytes.fromhex(os.environ["APPLICATION_SIGNATURE"])
        key = bytes.fromhex(os.environ["FALCON_VERIFICATION_KEY"])
    except (KeyError, ValueError):
        return False, "Checker not set up.", "Try again later."

    data = upload.read() if upload and upload.filename else b""
    if not data:
        return False, "No file received.", "Choose a file and try again."

    computed_hash = hashlib.sha256(data).digest()
    if not hmac.compare_digest(computed_hash, expected_hash):
        return False, "File does not match ours.", "Don't use it. Download it again."

    try:
        valid = falcon.verify(key, computed_hash, signature)
    except Exception:
        valid = False
    if not valid:
        return False, "Signature is not valid.", "Don't use it. Download it again."

    return True, "Hash and signature match.", "Safe to use."


@app.route("/", methods=["GET", "POST"])
def index():
    upload = request.files.get("binary")
    result = check(upload) if request.method == "POST" else None
    return render_template("index.html", result=result, filename=upload.filename if upload else None)


if __name__ == "__main__":
    app.run()
