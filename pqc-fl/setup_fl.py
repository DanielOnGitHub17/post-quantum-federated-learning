"""Start a federated-learning round on all configured nodes."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
import logging
import os
from typing import Any

import requests

import combsign
import kyber_cryptography

logger = logging.getLogger(__name__)

NODES = 6
COMPANY_NAMES = ("NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META")
REQUEST_TIMEOUT = (5, 300)


def node_endpoints() -> dict[str, str]:
    """Return one `/train/` endpoint for each company."""
    configured = os.getenv("NODE_ENDPOINTS")
    if not configured:
        raise ValueError("NODE_ENDPOINTS environment variable is required")

    endpoint_entries = [*map(str.strip, configured.split(","))]
    endpoints: dict[str, str] = {}
    for entry in endpoint_entries:
        parts = entry.split("->", 1)
        if len(parts) != 2:
            raise ValueError("NODE_ENDPOINTS entries must use the format COMPANY->URL")
        company, endpoint = map(str.strip, parts)
        if not company or not endpoint:
            raise ValueError("NODE_ENDPOINTS entries must use the format COMPANY->URL")
        if company not in COMPANY_NAMES:
            raise ValueError(f"Unsupported company in NODE_ENDPOINTS: {company}")
        if company in endpoints:
            raise ValueError(f"Duplicate company in NODE_ENDPOINTS: {company}")
        endpoints[company] = endpoint

    if len(endpoints) != NODES or set(endpoints) != set(COMPANY_NAMES):
        raise ValueError(
            f"NODE_ENDPOINTS must contain exactly one URL for each company: "
            f"{', '.join(COMPANY_NAMES)}"
        )
    return endpoints


def request_node(
    company: str,
    endpoint: str,
    public_key: str,
) -> str:
    logger.info("Sending training request: company=%s endpoint=%s", company, endpoint)
    response = requests.post(
        endpoint,
        json={
            "company_name": company,
            "public_key": public_key,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    logger.info(
        "Training request completed: company=%s http_status=%d",
        company,
        response.status_code,
    )

    payload = response.json()
    encrypted_result = payload.get("result")
    if not isinstance(encrypted_result, str):
        raise ValueError(f"Node {company} returned no encrypted result")

    return encrypted_result


def start_federated_learning() -> dict[str, Any]:
    """Request all PMOs concurrently, then combine only a complete round."""
    endpoints = node_endpoints()
    public_keys: dict[str, str] = {}
    private_keys: dict[str, bytes] = {}
    for company in endpoints:
        public_key, private_key = kyber_cryptography.generate_key_pair()
        public_keys[company] = base64.b64encode(public_key).decode("ascii")
        private_keys[company] = private_key
        logger.info("Generated Kyber key pair: company=%s", company)

    encrypted_results: dict[str, str] = {}
    results: dict[str, bytes] = {}
    failures: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=NODES) as executor:
        futures = {
            executor.submit(
                request_node,
                company,
                endpoint,
                public_keys[company],
            ): company
            for company, endpoint in endpoints.items()
        }

        for future in as_completed(futures):
            company = futures[future]
            try:
                encrypted_results[company] = future.result()
                logger.info(
                    "Encrypted node result received: company=%s results_received=%d/%d",
                    company,
                    len(encrypted_results),
                    NODES,
                )
            except (requests.RequestException, ValueError, TypeError) as error:
                failures[company] = str(error)
                logger.error("Node request failed: company=%s error=%s", company, error)

    for company, encrypted_result in encrypted_results.items():
        if company in failures:
            continue
        try:
            results[company] = kyber_cryptography.decrypt(
                encrypted_result,
                private_key=private_keys[company],
                company_name=company,
            )
            logger.info("Decrypted node result: company=%s", company)
        except (ValueError, TypeError) as error:
            failures[company] = str(error)
            logger.error(
                "Node result decryption failed: company=%s error=%s", company, error
            )

    if failures:
        logger.error(
            "Federated learning failed: results_received=%d/%d failures=%d",
            len(results),
            NODES,
            len(failures),
        )
        return {
            "status": "failed",
            "results_received": len(results),
            "failures": failures,
        }

    logger.info(
        "Combining node results: results_received=%d/%d",
        len(results),
        NODES,
    )
    artifacts = combsign.combine_pmos(results)
    logger.info(
        "Node results combined successfully: results_received=%d",
        len(results),
    )
    return {
        "status": "completed",
        "results_received": len(results),
        "artifacts": {name: str(path) for name, path in artifacts.items()},
    }
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    print(start_federated_learning())
