"""
Flask server that will receive URL of dataset, fetch it.
then transfer to the model to generate a Partial model output
"""

from flask import Flask, jsonify, request

import model


app = Flask(__name__)


@app.post("/train/")
def train():
	"""Start LSTM training when the node receives a training request."""
	payload = request.get_json(silent=True) or {}
	if not isinstance(payload, dict) or "company_name" not in payload:
		return jsonify({"error": "Request body must contain 'company_name'"}), 400

	result = model.train_lstm(payload["company_name"])

	return jsonify({"status": "training_completed", "result": result}), 200


@app.get("/health")
def health():
	return jsonify({"status": "ready"})


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)
