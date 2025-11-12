"""
TCDAFS - API Utilities
Contains helper functions for API communication
"""
import requests
import logging

from config.settings import API_URL

logger = logging.getLogger(__name__)


def make_api_request(endpoint, token=None, method="GET", data=None, timeout=5):
    """
    API request handler with proper error handling

    Args:
        endpoint: API endpoint path (e.g., "/stations")
        token: Authentication token dict with 'access_token' key
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
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
        elif response.status_code == 500:
            logger.error(f"API Server Error 500: {response.text}")
            try:
                error_data = response.json()
                return {"error": "server_error", "message": error_data.get("detail", "Internal server error"), "status_code": 500}
            except:
                return {"error": "server_error", "message": "Internal server error", "status_code": 500}
        else:
            logger.error(f"API Error {response.status_code}: {response.text}")
            try:
                error_data = response.json()
                return {"error": "api_error", "message": error_data.get("detail", response.text), "status_code": response.status_code}
            except:
                return {"error": "api_error", "message": response.text, "status_code": response.status_code}
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout for {endpoint}")
        return {"error": "timeout", "message": f"Request timed out after {timeout} seconds"}
    except Exception as e:
        logger.error(f"API request failed: {e}")
        return {"error": "connection_error", "message": str(e)}
