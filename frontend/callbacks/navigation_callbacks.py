"""
TCDAFS - Navigation Callbacks
Handle page routing and navigation between different pages
"""
from dash import callback, Input, Output, State, html, no_update
from utils.api import make_api_request
from config.styles import CONTENT_STYLE
from components.common.sidebar import create_sidebar
from components.auth.login import login_layout
from layouts import (
    overview_layout,
    ticket_layout,
    train_models_layout,
    trains_layout,
    routes_layout,
    train_schedules_layout,
    schedule_by_station_layout,
    ticket_pricing_layout,
    daily_schedules_layout
)
import logging

logger = logging.getLogger(__name__)


def register(app):
    """Register navigation callbacks with the app"""

    @callback(
        Output("page-content", "children"),
        [Input("url", "pathname"),
         Input("token-store", "data")],
        prevent_initial_call=False
    )
    def display_page(pathname, token):
        """
        Handle page routing based on URL pathname

        Args:
            pathname: Current URL pathname
            token: Authentication token data

        Returns:
            Page content with sidebar and main content area
        """
        if not token:
            return login_layout()

        # Default to "/" if pathname is None
        if not pathname:
            pathname = "/"

        # Use cached username from token instead of making API call every time
        username = token.get("username", "user@railway.lk")
        full_name = token.get("full_name", "Administrator")

        # Only fetch user data if not in token (optional - can be removed entirely)
        if not full_name or full_name == "Administrator":
            try:
                user_data = make_api_request("/users/me", token=token, timeout=2)
                if user_data and isinstance(user_data, dict):
                    full_name = user_data.get("full_name", "Administrator")
                    username = user_data.get("email", username)
            except Exception as e:
                logger.warning(f"Could not fetch user profile: {e}")
                # Use default values on error
                full_name = "Administrator"

        if pathname == "/tickets":
            content = ticket_layout()
        elif pathname == "/train-models":
            content = train_models_layout()
        elif pathname == "/trains":
            content = trains_layout()
        elif pathname == "/routes":
            content = routes_layout()
        elif pathname == "/schedules":
            content = train_schedules_layout()
        elif pathname == "/schedule-stations":
            content = schedule_by_station_layout()
        elif pathname == "/pricing":
            content = ticket_pricing_layout()
        elif pathname == "/daily-schedules":
            content = daily_schedules_layout()
        else:
            content = overview_layout()

        # Pass current pathname to sidebar for active state
        return html.Div([
            create_sidebar(email=username, full_name=full_name, current_path=pathname),
            html.Div(content, style=CONTENT_STYLE)
        ])

    @callback(
        Output("profile-dropdown-menu", "style"),
        Input("profile-dropdown-btn", "n_clicks"),
        State("profile-dropdown-menu", "style"),
        prevent_initial_call=True
    )
    def toggle_profile_dropdown(n_clicks, current_style):
        """
        Toggle profile dropdown visibility

        Args:
            n_clicks: Number of times profile button was clicked
            current_style: Current style of dropdown menu

        Returns:
            Updated style with display toggled
        """
        if n_clicks:
            if current_style.get("display") == "none":
                current_style["display"] = "block"
            else:
                current_style["display"] = "none"
            return current_style
        return no_update
