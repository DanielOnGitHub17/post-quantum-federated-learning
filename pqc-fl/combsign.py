"""Combine partial model outputs into one serialized aggregate."""

import base64
import hashlib
import pickle
from typing import Any


def combine_pmos(pmos: dict[str, bytes]) -> dict[str, Any]:
    """Bundle all PMOs and return a hash-addressed, JSON-safe result."""
    if not pmos:
        raise ValueError("At least one PMO is required")

    combined_model = pickle.dumps(
        {"models": dict(sorted(pmos.items()))},
        protocol=pickle.HIGHEST_PROTOCOL,
    )
    return {
        "sha256": hashlib.sha256(combined_model).hexdigest(),
        "model": base64.b64encode(combined_model).decode("ascii"),
        "model_bytes": len(combined_model),
    }
