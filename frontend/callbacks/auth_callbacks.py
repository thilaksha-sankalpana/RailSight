"""
TCDAFS - Authentication Callbacks
Handle user login and authentication
"""
from dash import callback, Input, Output, State, no_update
import requests
from config.settings import API_URL
import logging

logger = logging.getLogger(__name__)


def register(app):
    """Register authentication callbacks with the app"""

    @callback(
        [Output("token-store", "data"),
         Output("login-alert", "children"),
         Output("login-alert", "is_open"),
         Output("login-alert", "color"),
         Output("url", "pathname")],
        Input("login-button", "n_clicks"),
        [State("login-username", "value"),
         State("login-password", "value")],
        prevent_initial_call=True
    )
    def login(n_clicks, username, password):
        """
        Handle user login authentication

        Args:
            n_clicks: Number of times login button was clicked
            username: User's email/username
            password: User's password

        Returns:
            Tuple of (token_data, alert_message, alert_open, alert_color, redirect_path)
        """
        if not n_clicks:
            return no_update, "", False, "danger", no_update

        if not username or not password:
            return no_update, "Please enter email and password", True, "warning", no_update

        try:
            response = requests.post(
                f"{API_URL}/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=5
            )
            if response.status_code == 200:
                token_data = response.json()
                logger.info(f"User {username} logged in successfully")

                # Fetch user profile data once at login and cache it in token
                full_name = "Administrator"
                try:
                    from utils.api import make_api_request
                    user_data = make_api_request("/users/me", token={"access_token": token_data["access_token"]}, timeout=2)
                    if user_data and isinstance(user_data, dict):
                        full_name = user_data.get("full_name", "Administrator")
                except:
                    pass  # Use default if fetch fails

                return {
                    "access_token": token_data["access_token"],
                    "username": username,
                    "full_name": full_name  # Cache full name to avoid repeated API calls
                }, "", False, "success", "/"
            else:
                logger.warning(f"Failed login attempt for user {username}")
                return no_update, "Invalid email or password", True, "danger", no_update
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return no_update, f"Login failed: {str(e)}", True, "danger", no_update
