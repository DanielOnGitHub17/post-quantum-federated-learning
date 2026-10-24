"""
Flask server that will receive URL of dataset, fetch it.
then transfer to the model to generate a Partial model output
"""

import base64
import binascii

from flask import Flask, jsonify, request

import kyber_cryptography
import model

app = Flask(__name__)


@app.post("/train/")
def train():
    """Start LSTM training when the node receives a training request."""
    payload = request.get_json(silent=True) or {}
    if (
        not isinstance(payload, dict)
        or not {"company_name", "public_key"} <= payload.keys()
    ):
        return (
            jsonify(
                {"error": "Request body must contain 'company_name' and 'public_key'"}
            ),
            400,
        )

    try:
        public_key = base64.b64decode(payload["public_key"], validate=True)
    except (binascii.Error, ValueError, TypeError):
        return jsonify({"error": "public_key must be a valid Base64 string"}), 400

    model_bytes = model.train_lstm(payload["company_name"])
    encoded_model = base64.b64encode(model_bytes).decode("ascii")
    result = kyber_cryptography.encrypt(encoded_model.encode("ascii"), public_key)

    return jsonify({"status": "training_completed", "result": result}), 200


@app.get("/health")
def health():
    return jsonify({"status": "ready"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
