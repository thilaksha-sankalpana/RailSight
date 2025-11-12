"""
TCDAFS - Train Routes Management Page
Comprehensive railway route and station connectivity management
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.common.topbar import create_topbar
from config.styles import COLORS, BUTTON_PRIMARY


def routes_layout():
    """
    Create professional train routes management page with enhanced UI

    Returns:
        Dash HTML component for the routes page
    """
    return html.Div([
        create_topbar(),
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-route", style={
                            'fontSize': '36px',
                            'color': COLORS['primary'],
                            'marginRight': '20px'
                        }),
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    html.Div([
                        html.H3("Railway Route Management", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '32px',
                            'letterSpacing': '-0.5px'
                        }),
                        html.P("Configure and manage inter-station railway connections and routes", style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '15px',
                            'margin': '6px 0 0 0',
                            'fontWeight': '400'
                        })
                    ])
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '0'}),
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-plus-circle", style={'marginRight': '10px', 'fontSize': '16px'}),
                        "Create New Route"
                    ], id="add-route-btn", style={
                        **BUTTON_PRIMARY,
                        'fontSize': '15px',
                        'padding': '12px 24px',
                        'fontWeight': '600'
                    })
                ], style={'marginLeft': 'auto'})
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'background': f'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
                'padding': '32px 36px',
                'marginBottom': '32px',
                'borderRadius': '12px',
                'boxShadow': '0 2px 12px rgba(0,0,0,0.08)',
                'border': f'1px solid #e8e8e8'
            }),

            # Alert for CRUD operations
            dbc.Alert(id="route-alert", is_open=False, duration=4000, style={'marginBottom': '20px'}),

            # Routes Table
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-route", style={'marginRight': '12px', 'color': COLORS['primary'], 'fontSize': '18px'}),
                        html.H5("Railway Routes", style={'display': 'inline', 'margin': '0', 'fontWeight': '600', 'color': COLORS['text_primary']})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'padding': '18px 24px', 'borderBottom': f'2px solid #f0f0f0'}),
                html.Div([
                    html.Div(id="routes-table", style={'minHeight': '300px'})
                ], style={'padding': '0'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '12px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                'border': f'1px solid #e8e8e8',
                'overflow': 'hidden'
            }),

            # Add/Edit Route Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle([
                    html.I(className="fas fa-route", style={'marginRight': '10px', 'color': COLORS['primary']}),
                    html.Span(id="route-modal-title")
                ]), close_button=True),
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Route Name *", style={'fontWeight': '600', 'marginBottom': '10px', 'fontSize': '14px'}),
                            dbc.Input(
                                id="route-name",
                                type="text",
                                placeholder="e.g., Colombo Fort - Kandy Main Line",
                                style={'fontSize': '14px'}
                            ),
                        ], width=12),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Origin Station *", style={'fontWeight': '600', 'marginBottom': '10px', 'fontSize': '14px'}),
                            dcc.Dropdown(
                                id="route-origin",
                                placeholder="Search and select starting station...",
                                searchable=True,
                                style={'fontSize': '14px'}
                            ),
                            dbc.FormText("Type to search for stations", color="muted"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Destination Station *", style={'fontWeight': '600', 'marginBottom': '10px', 'fontSize': '14px'}),
                            dcc.Dropdown(
                                id="route-destination",
                                placeholder="Search and select end station...",
                                searchable=True,
                                style={'fontSize': '14px'}
                            ),
                            dbc.FormText("Type to search for stations", color="muted"),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Route Distance (km)", style={'fontWeight': '600', 'marginBottom': '10px', 'fontSize': '14px'}),
                            dbc.Input(
                                id="route-distance",
                                type="number",
                                placeholder="120",
                                min=0,
                                step=0.1,
                                style={'fontSize': '14px'}
                            ),
                            dbc.FormText("Total route distance in kilometers", color="muted"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Estimated Duration (minutes)", style={'fontWeight': '600', 'marginBottom': '10px', 'fontSize': '14px'}),
                            dbc.Input(
                                id="route-duration",
                                type="number",
                                placeholder="180",
                                min=0,
                                step=1,
                                style={'fontSize': '14px'}
                            ),
                            dbc.FormText("Average travel time in minutes", color="muted"),
                        ], width=6),
                    ], className="mb-3"),
                ]),
                dbc.ModalFooter([
                    dbc.Button([
                        html.I(className="fas fa-times", style={'marginRight': '8px'}),
                        "Cancel"
                    ], id="cancel-route-btn", color="secondary", outline=True, style={'fontWeight': '500'}),
                    dbc.Button([
                        html.I(className="fas fa-save", style={'marginRight': '8px'}),
                        "Save Route"
                    ], id="save-route-btn", style={**BUTTON_PRIMARY, 'fontWeight': '600'}),
                ])
            ], id="route-modal", size="lg", is_open=False),

            # Delete Confirmation Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Confirm Delete")),
                dbc.ModalBody([
                    html.I(className="fas fa-exclamation-triangle", style={
                        'fontSize': '48px',
                        'color': COLORS['warning'],
                        'display': 'block',
                        'textAlign': 'center',
                        'marginBottom': '16px'
                    }),
                    html.P("Are you sure you want to delete this route?", style={
                        'textAlign': 'center',
                        'fontSize': '16px',
                        'marginBottom': '8px'
                    }),
                    html.P(id="route-delete-name", style={
                        'textAlign': 'center',
                        'fontWeight': '600',
                        'color': COLORS['primary'],
                        'fontSize': '18px'
                    })
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-delete-route-btn", color="secondary", outline=True),
                    dbc.Button("Delete", id="confirm-delete-route-btn", color="danger"),
                ])
            ], id="route-delete-modal", is_open=False),

            # Hidden stores for state management
            dcc.Store(id="route-edit-id"),
            dcc.Store(id="route-delete-id"),
            dcc.Store(id="routes-refresh-trigger", data=0),
        ], style={'padding': '30px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
