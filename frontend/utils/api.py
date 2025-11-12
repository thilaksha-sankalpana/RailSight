"""
TCDAFS - API Utilities
Contains helper functions for API communication
"""
import requests
import logging

from config.settings import API_URL

logger = logging.getLogger(__name__)


def make_api_request(endpoint, method="GET", token=None, data=None, timeout=5):
    """
    API request handler with proper error handling

    Args:
        endpoint: API endpoint path (e.g., "/stations")
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        token: Authentication token dict with 'access_token' key
        data: Request payload for POST/PUT/PATCH
        timeout: Request timeout in seconds

    Returns:
        Response JSON data or None on error
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token.get('access_token', '')}"

        url = f"{API_URL}{endpoint}"
        logger.info(f"Making {method} request to {url}")

        if method == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(url, headers=headers, json=data, timeout=timeout)
        elif method == "PATCH":
            headers["Content-Type"] = "application/json"
            response = requests.patch(url, headers=headers, json=data, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return None

        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"API Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout for {endpoint}")
        return None
    except Exception as e:
        logger.error(f"API request failed: {e}")
        return None
