"""
TCDAFS - Ticket Booking Page
Ticket booking interface with search, passenger details, and cancellation
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from components.common.topbar import create_topbar
from config.styles import COLORS, BUTTON_PRIMARY


def ticket_layout():
    """
    Create ticket booking page with booking form and cancellation section

    Returns:
        Dash HTML component for the ticket booking page
    """
    return html.Div([
        create_topbar(),
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Profile Settings")),
            dbc.ModalBody([
                dbc.Label("Full Name"),
                dbc.Input(id="profile-name", type="text", className="mb-3"),
                dbc.Label("Email"),
                dbc.Input(id="profile-email", type="email", className="mb-3", disabled=True),
                dbc.Label("Contact Number"),
                dbc.Input(id="profile-contact", type="text", className="mb-3"),
            ]),
            dbc.ModalFooter([
                dbc.Button("Save Changes", id="save-profile-btn", color="primary"),
                dbc.Button("Close", id="close-profile-modal", className="ms-auto")
            ])
        ], id="profile-modal", is_open=False, className="fade-in"),
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Change Password")),
            dbc.ModalBody([
                dbc.Alert(id="password-alert", is_open=False, duration=3000),
                dbc.Label("Current Password"),
                dbc.Input(id="current-password", type="password", className="mb-3"),
                dbc.Label("New Password"),
                dbc.Input(id="new-password", type="password", className="mb-3"),
                dbc.Label("Confirm New Password"),
                dbc.Input(id="confirm-password", type="password", className="mb-3"),
            ]),
            dbc.ModalFooter([
                dbc.Button("Change Password", id="save-password-btn", color="primary"),
                dbc.Button("Close", id="close-password-modal", className="ms-auto")
            ])
        ], id="password-modal", is_open=False, className="fade-in"),
        
        # Thermal Print Ticket Modal
        dbc.Modal([
            dbc.ModalBody([
                html.Div(id="thermal-print-content", style={
                    'fontFamily': 'monospace',
                    'background': 'white',
                    'padding': '20px',
                    'maxWidth': '400px',
                    'margin': '0 auto'
                })
            ], style={'padding': '0', 'background': '#f5f5f5'}),
            dbc.ModalFooter([
                dbc.Button([
                    html.I(className="fas fa-print", style={'marginRight': '8px'}),
                    "Print Ticket"
                ], id="print-ticket-btn", color="primary"),
                dbc.Button("Close", id="close-ticket-modal", className="ms-2")
            ])
        ], id="ticket-print-modal", is_open=False, size="lg", className="fade-in"),
        
        html.Div([
            html.H4("Ticket Booking", style={
                'color': COLORS['text_primary'],
                'fontWeight': '700',
                'marginBottom': '24px'
            }),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("Book New Ticket", style={
                            'padding': '20px',
                            'borderBottom': f'1px solid {COLORS["border"]}',
                            'margin': '0'
                        }),
                        html.Div([
                            dbc.Alert(id="ticket-alert", is_open=False, duration=4000, style={'marginBottom': '16px'}),

                            # Step 1: Route Selection
                            html.Div([
                                html.H6([
                                    html.I(className="fas fa-route", style={'marginRight': '8px'}),
                                    "Step 1: Select Route & Date"
                                ], style={'color': COLORS['primary'], 'fontWeight': '600', 'marginBottom': '16px'}),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Origin Station *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                                        dcc.Dropdown(
                                            id="ticket-origin",
                                            placeholder="Select departure station...",
                                            searchable=True,
                                            style={'marginBottom': '8px'}
                                        ),
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Destination Station *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                                        dcc.Dropdown(
                                            id="ticket-destination",
                                            placeholder="Select arrival station...",
                                            searchable=True,
                                            style={'marginBottom': '8px'}
                                        ),
                                    ], width=6),
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Travel Date *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                                        dbc.Input(
                                            id="ticket-date",
                                            type="date",
                                            value=datetime.now().strftime("%Y-%m-%d"),
                                            style={'marginBottom': '8px'}
                                        ),
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Travel Time", style={'fontWeight': '500', 'marginBottom': '8px'}),
                                        dbc.Input(
                                            id="ticket-time",
                                            type="time",
                                            placeholder="Select time...",
                                            style={'marginBottom': '8px'}
                                        ),
                                    ], width=6),
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button([
                                            html.I(className="fas fa-search", style={'marginRight': '10px'}),
                                            "Search Trains"
                                        ], id="search-trains-btn", style={
                                            **BUTTON_PRIMARY,
                                            'width': '100%',
                                            'marginTop': '8px',
                                            'padding': '12px 24px',
                                            'fontSize': '15px',
                                            'fontWeight': '600'
                                        }),
                                    ], width=12),
                                ]),
                            ], style={
                                'padding': '16px',
                                'background': '#fafbfc',
                                'borderRadius': '8px',
                                'marginBottom': '20px',
                                'border': f'1px solid {COLORS["border"]}'
                            }),

                            # Step 2: Train Selection
                            html.Div([
                                html.H6([
                                    html.I(className="fas fa-train", style={'marginRight': '8px'}),
                                    "Step 2: Choose Train"
                                ], style={'color': COLORS['primary'], 'fontWeight': '600', 'marginBottom': '16px'}),
                                html.Div(id="available-schedules")
                            ], style={
                                'padding': '16px',
                                'background': '#fafbfc',
                                'borderRadius': '8px',
                                'marginBottom': '20px',
                                'border': f'1px solid {COLORS["border"]}'
                            }),

                            # Step 3: Booking Details
                            html.Div([
                                html.H6([
                                    html.I(className="fas fa-ticket-alt", style={'marginRight': '8px'}),
                                    "Step 3: Booking Details"
                                ], style={'color': COLORS['primary'], 'fontWeight': '600', 'marginBottom': '16px'}),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Class *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                                        dcc.Dropdown(
                                            id="ticket-class",
                                            options=[
                                                {"label": "1st Class", "value": "First"},
                                                {"label": "2nd Class", "value": "Second"},
                                                {"label": "3rd Class", "value": "Third"}
                                            ],
                                            value="Third",
                                            clearable=False
                                        ),
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Label("Number of Passengers *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                                        html.Div([
                                            html.Button([
                                                html.I(className="fas fa-minus")
                                            ], id="decrease-tickets", style={
                                                'background': COLORS['primary'],
                                                'color': 'white',
                                                'border': 'none',
                                                'padding': '10px 14px',
                                                'borderRadius': '8px 0 0 8px',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.2s'
                                            }),
                                            html.Span("1", id="ticket-count", style={
                                                'display': 'inline-block',
                                                'padding': '10px 24px',
                                                'background': '#f1f5f9',
                                                'fontWeight': '600',
                                                'minWidth': '70px',
                                                'textAlign': 'center',
                                                'fontSize': '16px'
                                            }),
                                            html.Button([
                                                html.I(className="fas fa-plus")
                                            ], id="increase-tickets", style={
                                                'background': COLORS['primary'],
                                                'color': 'white',
                                                'border': 'none',
                                                'padding': '10px 14px',
                                                'borderRadius': '0 8px 8px 0',
                                                'cursor': 'pointer',
                                                'transition': 'all 0.2s'
                                            })
                                        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
                                    ], width=6),
                                ]),
                            ], style={
                                'padding': '16px',
                                'background': '#fafbfc',
                                'borderRadius': '8px',
                                'marginBottom': '16px',
                                'border': f'1px solid {COLORS["border"]}'
                            }),
                            html.Div(id="passenger-details-container", style={'marginBottom': '16px'}),
                            html.Div([
                                html.Span("Total Price: ", style={'fontSize': '14px'}),
                                html.Span(id="ticket-price", children="LKR 0.00", style={
                                    'color': COLORS['primary'],
                                    'fontSize': '24px',
                                    'fontWeight': '700'
                                })
                            ], style={
                                'background': '#f1f5f9',
                                'padding': '16px',
                                'borderRadius': '8px',
                                'textAlign': 'center',
                                'marginBottom': '16px'
                            }),
                            dbc.Button([
                                html.I(className="fas fa-ticket-alt", style={'marginRight': '8px'}),
                                "Book Tickets"
                            ], id="book-ticket-btn", style={
                                **BUTTON_PRIMARY,
                                'width': '100%'
                            }),
                            dcc.Store(id="selected-schedule-store"),
                            dcc.Store(id="ticket-count-store", data=1),
                            dcc.Store(id="booked-tickets-store"),  # Store booked ticket data
                        ], style={'padding': '20px'})
                    ], style={
                        'background': COLORS['surface'],
                        'borderRadius': '12px',
                        'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                        'border': f'1px solid {COLORS["border"]}'
                    })
                ], width=8),
                dbc.Col([
                    html.Div([
                        html.H6("Ticket Refund / Cancel", style={
                            'padding': '20px',
                            'borderBottom': f'1px solid {COLORS["border"]}',
                            'margin': '0'
                        }),
                        html.Div([
                            dbc.Alert(id="cancel-ticket-alert", is_open=False, duration=4000),
                            dbc.Label("Ticket ID *", style={'fontWeight': '500', 'fontSize': '13px'}),
                            dbc.Input(
                                id="cancel-ticket-id",
                                placeholder="Enter Ticket ID (e.g., TKT-001)",
                                style={'borderRadius': '6px', 'marginBottom': '12px'}
                            ),
                            dbc.Label("NIC/Passport for Verification *", style={'fontWeight': '500', 'fontSize': '13px'}),
                            dbc.Input(
                                id="cancel-nic-passport",
                                placeholder="Enter NIC or Passport",
                                style={'borderRadius': '6px', 'marginBottom': '12px'}
                            ),
                            dbc.Button([
                                html.I(className="fas fa-search", style={'marginRight': '8px'}),
                                "Verify Ticket"
                            ], id="verify-ticket-btn", color="info", style={
                                'width': '100%',
                                'marginBottom': '16px'
                            }),
                            html.Div(id="ticket-details-display", style={'marginBottom': '12px'}),
                            dbc.Label("Change Ticket Status", style={'fontWeight': '500', 'fontSize': '13px'}),
                            dcc.Dropdown(
                                id="cancel-ticket-status",
                                options=[
                                    {"label": "Cancelled", "value": "Cancelled"},
                                    {"label": "Refunded", "value": "Refunded"},
                                    {"label": "Pending", "value": "Pending"},
                                    {"label": "Completed", "value": "Completed"},
                                    {"label": "No-Show", "value": "No-Show"}
                                ],
                                placeholder="Select new status...",
                                style={'marginBottom': '16px'}
                            ),
                            dbc.Button([
                                html.I(className="fas fa-ban", style={'marginRight': '8px'}),
                                "Update Ticket Status"
                            ], id="update-ticket-status-btn", color="danger", style={
                                'width': '100%'
                            }, disabled=True),
                            dcc.Store(id="verified-ticket-store")
                        ], style={'padding': '20px'})
                    ], style={
                        'background': COLORS['surface'],
                        'borderRadius': '12px',
                        'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                        'border': f'1px solid {COLORS["border"]}'
                    })
                ], width=4)
            ])
        ], style={'padding': '30px'})
    ])
