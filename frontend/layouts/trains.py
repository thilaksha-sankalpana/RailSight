"""
TCDAFS - Operational Trains Management Page
Manage active trains in the railway system
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.common.topbar import create_topbar
from config.styles import COLORS, BUTTON_PRIMARY


def trains_layout():
    """
    Create operational trains management page

    Returns:
        Dash HTML component for the operational trains page
    """
    return html.Div([
        create_topbar(),
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-subway", style={
                            'fontSize': '36px',
                            'color': COLORS['primary'],
                            'marginRight': '20px'
                        }),
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    html.Div([
                        html.H3("Operational Trains", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '32px',
                            'letterSpacing': '-0.5px'
                        }),
                        html.P("Monitor and manage operational train fleet", style={
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
                        "Add Train"
                    ], id="add-operational-train-btn", style={
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
            dbc.Alert(id="operational-train-alert", is_open=False, duration=4000, style={'marginBottom': '20px'}),

            # Filter Section
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-filter", style={'marginRight': '10px', 'color': COLORS['primary'], 'fontSize': '18px'}),
                        html.H5("Filters", style={'display': 'inline', 'margin': '0', 'fontWeight': '600', 'color': COLORS['text_primary']})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'padding': '18px 24px', 'borderBottom': f'2px solid #f0f0f0'}),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Train Model", style={'fontWeight': '600', 'marginBottom': '10px', 'fontSize': '13px', 'color': COLORS['text_secondary']}),
                            dcc.Dropdown(
                                id="filter-operational-train-model",
                                placeholder="All Models",
                                clearable=True,
                                style={'fontSize': '14px'}
                            ),
                        ], width=5),
                        dbc.Col([
                            dbc.Label("Status", style={'fontWeight': '600', 'marginBottom': '10px', 'fontSize': '13px', 'color': COLORS['text_secondary']}),
                            dcc.Dropdown(
                                id="filter-operational-train-status",
                                options=[
                                    {"label": "Active", "value": "Active"},
                                    {"label": "Maintenance", "value": "Maintenance"},
                                    {"label": "Inactive", "value": "Inactive"},
                                    {"label": "Retired", "value": "Retired"}
                                ],
                                placeholder="All Statuses",
                                clearable=True,
                                style={'fontSize': '14px'}
                            ),
                        ], width=5),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-redo", style={'marginRight': '8px'}),
                                "Reset"
                            ], id="clear-operational-train-filters",
                            color="light",
                            style={
                                'marginTop': '32px',
                                'width': '100%',
                                'fontWeight': '500',
                                'border': f'1px solid {COLORS["border"]}',
                                'color': COLORS['text_secondary']
                            })
                        ], width=2),
                    ])
                ], style={'padding': '24px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '12px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                'border': f'1px solid #e8e8e8',
                'marginBottom': '24px'
            }),

            # Operational Trains Table
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-train", style={'marginRight': '12px', 'color': COLORS['primary'], 'fontSize': '18px'}),
                        html.H5("Operational Trains", style={'display': 'inline', 'margin': '0', 'fontWeight': '600', 'color': COLORS['text_primary']})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'padding': '18px 24px', 'borderBottom': f'2px solid #f0f0f0'}),
                html.Div([
                    html.Div(id="trains-table", style={'minHeight': '300px'})
                ], style={'padding': '0'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '12px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                'border': f'1px solid #e8e8e8',
                'overflow': 'hidden'
            }),

            # Add Train Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle([
                    html.I(className="fas fa-plus-circle", style={'marginRight': '10px', 'color': COLORS['primary']}),
                    "Add Operational Trains"
                ]), close_button=True),
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Train Model *", style={'fontWeight': '600', 'marginBottom': '10px', 'fontSize': '14px'}),
                            dcc.Dropdown(
                                id="operational-train-model",
                                placeholder="Select train model...",
                                style={'fontSize': '14px'}
                            ),
                        ], width=12),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Compartments per Unit", style={'fontWeight': '600', 'marginBottom': '10px', 'fontSize': '14px'}),
                            dbc.Input(
                                id="operational-train-compartments",
                                type="number",
                                disabled=True,
                                placeholder="Auto-filled from model",
                                style={'backgroundColor': '#f5f5f5', 'fontSize': '14px'}
                            ),
                            dbc.FormText("Automatically filled based on selected model", color="muted"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Quantity *", style={'fontWeight': '600', 'marginBottom': '10px', 'fontSize': '14px'}),
                            dbc.Input(
                                id="operational-train-quantity",
                                type="number",
                                min=1,
                                max=50,
                                value=1,
                                placeholder="e.g., 5",
                                style={'fontSize': '14px'}
                            ),
                            dbc.FormText("Number of trains to create (max 50)", color="muted"),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Initial Status", style={'fontWeight': '600', 'marginBottom': '10px', 'fontSize': '14px'}),
                            dcc.Dropdown(
                                id="operational-train-status",
                                options=[
                                    {"label": "Active", "value": "Active"},
                                    {"label": "Maintenance", "value": "Maintenance"},
                                    {"label": "Inactive", "value": "Inactive"}
                                ],
                                value="Active",
                                style={'fontSize': '14px'}
                            ),
                        ], width=12),
                    ], className="mb-3"),
                    html.Div(id="train-id-preview", style={'marginTop': '20px'}),
                ]),
                dbc.ModalFooter([
                    dbc.Button([
                        html.I(className="fas fa-times", style={'marginRight': '8px'}),
                        "Cancel"
                    ], id="cancel-operational-train-btn", color="secondary", outline=True, style={'fontWeight': '500'}),
                    dbc.Button([
                        html.I(className="fas fa-check", style={'marginRight': '8px'}),
                        "Add Trains"
                    ], id="save-operational-train-btn", style={**BUTTON_PRIMARY, 'fontWeight': '600'}),
                ])
            ], id="operational-train-modal", size="lg", is_open=False),

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
                    html.P("Are you sure you want to delete this operational train?", style={
                        'textAlign': 'center',
                        'fontSize': '16px',
                        'marginBottom': '8px'
                    }),
                    html.P(id="operational-train-delete-name", style={
                        'textAlign': 'center',
                        'fontWeight': '600',
                        'color': COLORS['primary'],
                        'fontSize': '18px'
                    })
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-delete-operational-train-btn", color="secondary", outline=True),
                    dbc.Button("Delete", id="confirm-delete-operational-train-btn", color="danger"),
                ])
            ], id="operational-train-delete-modal", is_open=False),

            # Hidden store to trigger table refresh after operations
            dcc.Store(id="trains-refresh-trigger", data=0),

        ], style={'padding': '30px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
