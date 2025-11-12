"""
TCDAFS - Profile Callbacks
Handle user profile and password change modals
"""
from dash import callback, Input, Output, State, no_update
import logging

logger = logging.getLogger(__name__)


def register(app):
    """Register profile callbacks with the app"""

    @callback(
        Output("profile-modal", "is_open"),
        [Input("profile-link", "n_clicks"),
         Input("close-profile-modal", "n_clicks"),
         Input("save-profile-btn", "n_clicks")],
        State("profile-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_profile_modal(open_clicks, close_clicks, save_clicks, is_open):
        """Toggle profile settings modal"""
        return not is_open

    @callback(
        Output("password-modal", "is_open"),
        [Input("password-link", "n_clicks"),
         Input("close-password-modal", "n_clicks"),
         Input("save-password-btn", "n_clicks")],
        State("password-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_password_modal(open_clicks, close_clicks, save_clicks, is_open):
        """Toggle change password modal"""
        return not is_open
