"""
Flask server that will receive URL of dataset, fetch it.
then transfer to the model to generate a Partial model output
"""

import base64
import binascii
import logging

from flask import Flask, jsonify, request

import kyber_cryptography
import model

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@app.post("/train/")
def train():
    """Start LSTM training when the node receives a training request."""
    logger.info("Received training request")
    payload = request.get_json(silent=True) or {}
    if (
        not isinstance(payload, dict)
        or not {"company_name", "public_key"} <= payload.keys()
    ):
        logger.warning("Rejected training request: missing required fields")
        return (
            jsonify(
                {"error": "Request body must contain 'company_name' and 'public_key'"}
            ),
            400,
        )

    try:
        public_key = base64.b64decode(payload["public_key"], validate=True)
    except (binascii.Error, ValueError, TypeError):
        logger.warning("Rejected training request: invalid public key encoding")
        return jsonify({"error": "public_key must be a valid Base64 string"}), 400

    company = payload["company_name"]
    logger.info("Starting training workflow for company=%s", company)
    model_bytes = model.train_lstm(company)
    logger.info("Model ready; encrypting %d model bytes", len(model_bytes))
    result = kyber_cryptography.encrypt(model_bytes, public_key)
    logger.info("Training workflow completed for company=%s", company)

    return jsonify({"status": "training_completed", "result": result}), 200


@app.get("/health")
def health():
    logger.info("Health check requested")
    return jsonify({"status": "ready"})


if __name__ == "__main__":
    logger.info("Starting FL node server on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
