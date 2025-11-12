"""
TCDAFS - Ticket Verification Callbacks
Handle ticket verification and status updates (cancellation/refund)
"""
from dash import callback, Input, Output, State, html, no_update
import dash_bootstrap_components as dbc
from utils.api import make_api_request
from config.styles import COLORS
import logging

logger = logging.getLogger(__name__)


def register(app):
    """Register ticket verification callbacks with the app"""

    @callback(
        [Output("cancel-ticket-alert", "children"),
         Output("cancel-ticket-alert", "is_open"),
         Output("cancel-ticket-alert", "color"),
         Output("ticket-details-display", "children"),
         Output("update-ticket-status-btn", "disabled"),
         Output("verified-ticket-store", "data")],
        Input("verify-ticket-btn", "n_clicks"),
        [State("cancel-ticket-id", "value"),
         State("cancel-nic-passport", "value"),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def verify_ticket_for_cancel(n, ticket_id, nic_passport, token):
        """Verify ticket by ID and NIC/Passport"""
        if not n or not token:
            return "", False, "danger", html.Div(), True, None

        if not ticket_id or not nic_passport:
            return "Please enter both Ticket ID and NIC/Passport", True, "warning", html.Div(), True, None

        # Fetch ticket from backend
        ticket = make_api_request(f"/tickets/{ticket_id}", token=token)

        if not ticket:
            return f"Ticket {ticket_id} not found", True, "danger", html.Div(), True, None

        # Verify NIC/Passport matches (v2.0: separate fields)
        ticket_nic = ticket.get('nic')
        ticket_passport = ticket.get('passport')

        # Check if provided value matches either NIC or Passport
        if not (ticket_nic == nic_passport or ticket_passport == nic_passport):
            return "NIC/Passport does not match ticket records", True, "danger", html.Div(), True, None

        # Fetch station names
        origin_id = ticket.get('origin_station_id')
        destination_id = ticket.get('destination_station_id')

        origin_station = make_api_request(f"/stations/{origin_id}", token=token) if origin_id else None
        destination_station = make_api_request(f"/stations/{destination_id}", token=token) if destination_id else None

        origin_name = origin_station.get('station_name', origin_id) if origin_station else origin_id
        destination_name = destination_station.get('station_name', destination_id) if destination_station else destination_id

        # Display ticket details
        ticket_info = html.Div([
            html.Div([
                html.Strong("Ticket Verified", style={'color': COLORS['success'], 'fontSize': '14px'}),
            ], style={'marginBottom': '12px'}),
            html.Div([
                html.P([html.Strong("Ticket ID: "), ticket.get('ticket_id')], style={'margin': '4px 0', 'fontSize': '13px'}),
                html.P([html.Strong("Route: "), f"{origin_name} → {destination_name}"],
                       style={'margin': '4px 0', 'fontSize': '13px'}),
                html.P([html.Strong("Schedule Date: "), str(ticket.get('schedule_date'))],
                       style={'margin': '4px 0', 'fontSize': '13px'}),
                html.P([html.Strong("Class: "), str(ticket.get('class'))],
                       style={'margin': '4px 0', 'fontSize': '13px'}),
                html.P([html.Strong("Fee: "), f"LKR {ticket.get('fee', 0)}"],
                       style={'margin': '4px 0', 'fontSize': '13px', 'fontWeight': '600', 'color': COLORS['primary']}),
                html.P([html.Strong("Current Status: "), str(ticket.get('status'))],
                       style={'margin': '4px 0', 'fontSize': '13px', 'color': COLORS['info']})
            ], style={
                'padding': '12px',
                'background': '#f8fafc',
                'borderRadius': '8px',
                'border': f'1px solid {COLORS["border"]}'
            })
        ])

        return "Ticket verified successfully. You can now update the status.", True, "success", ticket_info, False, ticket

    @callback(
        [Output("cancel-ticket-alert", "children", allow_duplicate=True),
         Output("cancel-ticket-alert", "is_open", allow_duplicate=True),
         Output("cancel-ticket-alert", "color", allow_duplicate=True),
         Output("cancel-ticket-id", "value"),
         Output("cancel-nic-passport", "value"),
         Output("cancel-ticket-status", "value"),
         Output("ticket-details-display", "children", allow_duplicate=True),
         Output("update-ticket-status-btn", "disabled", allow_duplicate=True)],
        Input("update-ticket-status-btn", "n_clicks"),
        [State("verified-ticket-store", "data"),
         State("cancel-ticket-status", "value"),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def update_ticket_status(n, verified_ticket, new_status, token):
        """Update ticket status (cancel/refund)"""
        if not n or not token:
            return "", False, "danger", no_update, no_update, no_update, no_update, no_update

        if not verified_ticket:
            return "Please verify a ticket first", True, "warning", no_update, no_update, no_update, no_update, no_update

        if not new_status:
            return "Please select a new status", True, "warning", no_update, no_update, no_update, no_update, no_update

        ticket_id = verified_ticket.get('ticket_id')

        # Update ticket status via backend API
        result = make_api_request(
            f"/tickets/{ticket_id}",
            method="PATCH",
            token=token,
            data={"status": new_status}
        )

        if result:
            return f"Ticket {ticket_id} status updated to {new_status}", True, "success", "", "", None, html.Div(), True
        else:
            return f"Failed to update ticket status", True, "danger", no_update, no_update, no_update, no_update, no_update
