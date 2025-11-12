"""
TCDAFS - Clientside Callbacks
JavaScript callbacks that run in the browser
"""
from dash import Output, Input
import logging

logger = logging.getLogger(__name__)


def register(app):
    """Register clientside callbacks with the app"""

    # Logout clientside callback - clears session and redirects
    app.clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks) {
                sessionStorage.clear();
                window.location.href = "/";
                return null;
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("token-store", "data", allow_duplicate=True),
        Input("logout-btn", "n_clicks"),
        prevent_initial_call=True
    )

    # Print ticket clientside callback - triggers browser print dialog
    app.clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks) {
                window.print();
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("print-ticket-btn", "n_clicks", allow_duplicate=True),
        Input("print-ticket-btn", "n_clicks"),
        prevent_initial_call=True
    )

    # Debug callback for save button
    app.clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks) {
                console.log("🔴 SAVE BUTTON CLICKED! n_clicks =", n_clicks);
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("save-train-model-btn", "n_clicks", allow_duplicate=True),
        Input("save-train-model-btn", "n_clicks"),
        prevent_initial_call=True
    )

    logger.info("Clientside callbacks registered")
