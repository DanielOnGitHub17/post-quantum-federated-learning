"""
Stock market prediction from daily values over the years.

"""

NODES = 6
# From NASDAQ
COMPANY_NAMES = {
    "NVDA": "NVIDIA",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet Class A",
    "AMZN": "Amazon",
    "META": "Meta Platforms",
}
data_set_urls = {"MSFT": ..., "GOOGL": ...}  # Up to 6
nodes_endpoints = {"MSFT": ..., "GOOGL": ...}

# Concurrently start requests to every node for it to start the implementation
