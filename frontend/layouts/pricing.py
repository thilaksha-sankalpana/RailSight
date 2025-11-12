"""
TCDAFS - Ticket Pricing Management Page
Manage ticket pricing for different routes and classes
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.common.topbar import create_topbar
from config.styles import COLORS, BUTTON_PRIMARY


def ticket_pricing_layout():
    """
    Create ticket pricing management page

    Returns:
        Dash HTML component for the pricing page
    """
    return html.Div([
        create_topbar(),
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.I(className="fas fa-tags", style={
                        'fontSize': '36px',
                        'color': COLORS['primary'],
                        'marginRight': '18px'
                    }),
                    html.Div([
                        html.H3("Ticket Pricing Management", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '30px',
                            'letterSpacing': '-0.5px'
                        }),
                        html.P("Search and manage ticket pricing across all routes and travel classes", style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '15px',
                            'margin': '6px 0 0 0',
                            'fontWeight': '400'
                        })
                    ])
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '0'})
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'background': f'linear-gradient(135deg, {COLORS["surface"]} 0%, #ffffff 100%)',
                'padding': '28px 32px',
                'marginBottom': '32px',
                'borderRadius': '16px',
                'boxShadow': '0 6px 20px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Alert for CRUD operations
            dbc.Alert(id="pricing-alert", is_open=False, duration=4000, style={'marginBottom': '20px'}),

            # Search/Filter Section
            html.Div([
                html.Div([
                    html.I(className="fas fa-filter", style={'marginRight': '12px', 'color': COLORS['primary'], 'fontSize': '18px'}),
                    html.H5("Search Pricing", style={'display': 'inline', 'margin': '0', 'fontWeight': '600', 'fontSize': '18px', 'color': COLORS['text_primary']})
                ], style={'padding': '22px 24px', 'borderBottom': f'2px solid {COLORS["border"]}'}),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-map-marker-alt", style={'marginRight': '8px', 'color': '#059669', 'fontSize': '12px'}),
                                "Origin Station"
                            ], style={'fontWeight': '600', 'marginBottom': '10px', 'color': COLORS['text_primary'], 'fontSize': '14px'}),
                            dcc.Dropdown(
                                id="filter-pricing-origin",
                                placeholder="Search origin station...",
                                clearable=True,
                                searchable=True,
                                optionHeight=50
                            ),
                        ], width=4),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-map-marker-alt", style={'marginRight': '8px', 'color': '#dc2626', 'fontSize': '12px'}),
                                "Destination Station"
                            ], style={'fontWeight': '600', 'marginBottom': '10px', 'color': COLORS['text_primary'], 'fontSize': '14px'}),
                            dcc.Dropdown(
                                id="filter-pricing-destination",
                                placeholder="Search destination station...",
                                clearable=True,
                                searchable=True,
                                optionHeight=50
                            ),
                        ], width=4),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-search", style={'marginRight': '10px'}),
                                "Search Pricing"
                            ], id="apply-pricing-filter", style={**BUTTON_PRIMARY, 'marginTop': '32px', 'width': '100%', 'padding': '10px 20px', 'fontSize': '15px', 'fontWeight': '600'}),
                        ], width=2),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-redo", style={'marginRight': '10px'}),
                                "Reset"
                            ], id="clear-pricing-filter", color="secondary", outline=True, style={'marginTop': '32px', 'width': '100%', 'padding': '10px 20px', 'fontSize': '15px', 'fontWeight': '600'}),
                        ], width=2),
                    ])
                ], style={'padding': '24px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}',
                'marginBottom': '28px'
            }),

            # Pricing Table
            html.Div([
                html.Div([
                    html.I(className="fas fa-list-alt", style={'marginRight': '12px', 'color': COLORS['primary'], 'fontSize': '18px'}),
                    html.H5("Pricing Results", style={'display': 'inline', 'margin': '0', 'fontWeight': '600', 'fontSize': '18px', 'color': COLORS['text_primary']})
                ], style={'padding': '22px 24px', 'borderBottom': f'2px solid {COLORS["border"]}'}),
                html.Div([
                    html.Div(id="pricing-table", style={'minHeight': '400px'})
                ], style={'padding': '0'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Edit Pricing Modal
            dbc.Modal([
                dbc.ModalHeader([
                    dbc.ModalTitle([
                        html.I(className="fas fa-edit", style={'marginRight': '12px', 'color': COLORS['primary']}),
                        "Edit Ticket Pricing"
                    ])
                ]),
                dbc.ModalBody([
                    # Hidden field to store pricing ID
                    html.Div(id="edit-pricing-id", style={'display': 'none'}),
                    
                    # Route Information Section
                    html.Div([
                        html.H6([
                            html.I(className="fas fa-route", style={'marginRight': '8px', 'color': COLORS['primary'], 'fontSize': '14px'}),
                            "Route Information"
                        ], style={'fontWeight': '600', 'marginBottom': '16px', 'color': COLORS['text_primary'], 'fontSize': '15px'}),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label([
                                    html.I(className="fas fa-map-marker-alt", style={'marginRight': '6px', 'color': '#059669', 'fontSize': '11px'}),
                                    "Origin Station"
                                ], style={'fontWeight': '500', 'marginBottom': '8px', 'fontSize': '13px', 'color': COLORS['text_secondary']}),
                                html.Div(id="edit-pricing-origin-name", style={
                                    'padding': '10px 14px',
                                    'background': '#f8f9fa',
                                    'borderRadius': '8px',
                                    'border': f'1px solid {COLORS["border"]}',
                                    'color': COLORS['text_primary'],
                                    'fontWeight': '500',
                                    'fontSize': '14px'
                                })
                            ], width=6),
                            dbc.Col([
                                dbc.Label([
                                    html.I(className="fas fa-map-marker-alt", style={'marginRight': '6px', 'color': '#dc2626', 'fontSize': '11px'}),
                                    "Destination Station"
                                ], style={'fontWeight': '500', 'marginBottom': '8px', 'fontSize': '13px', 'color': COLORS['text_secondary']}),
                                html.Div(id="edit-pricing-destination-name", style={
                                    'padding': '10px 14px',
                                    'background': '#f8f9fa',
                                    'borderRadius': '8px',
                                    'border': f'1px solid {COLORS["border"]}',
                                    'color': COLORS['text_primary'],
                                    'fontWeight': '500',
                                    'fontSize': '14px'
                                })
                            ], width=6),
                        ]),
                    ], style={'marginBottom': '24px', 'padding': '20px', 'background': '#fafbfc', 'borderRadius': '10px', 'border': f'1px solid {COLORS["border"]}'}),
                    
                    # Distance Section
                    html.Div([
                        html.H6([
                            html.I(className="fas fa-road", style={'marginRight': '8px', 'color': COLORS['primary'], 'fontSize': '14px'}),
                            "Distance"
                        ], style={'fontWeight': '600', 'marginBottom': '16px', 'color': COLORS['text_primary'], 'fontSize': '15px'}),
                        
                        dbc.Label("Distance (km) *", style={'fontWeight': '500', 'marginBottom': '8px', 'fontSize': '13px', 'color': COLORS['text_secondary']}),
                        dbc.Input(id="edit-pricing-distance", type="number", placeholder="Enter distance in kilometers", min=0, step=0.1),
                    ], style={'marginBottom': '24px'}),
                    
                    # Pricing Section
                    html.Div([
                        html.H6([
                            html.I(className="fas fa-dollar-sign", style={'marginRight': '8px', 'color': COLORS['primary'], 'fontSize': '14px'}),
                            "Class Fees"
                        ], style={'fontWeight': '600', 'marginBottom': '16px', 'color': COLORS['text_primary'], 'fontSize': '15px'}),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("1st Class Fee (LKR) *", style={'fontWeight': '500', 'marginBottom': '8px', 'fontSize': '13px', 'color': COLORS['text_secondary']}),
                                dbc.Input(id="edit-pricing-first-class", type="number", placeholder="0.00", min=0, step=0.01),
                            ], width=4),
                            dbc.Col([
                                dbc.Label("2nd Class Fee (LKR) *", style={'fontWeight': '500', 'marginBottom': '8px', 'fontSize': '13px', 'color': COLORS['text_secondary']}),
                                dbc.Input(id="edit-pricing-second-class", type="number", placeholder="0.00", min=0, step=0.01),
                            ], width=4),
                            dbc.Col([
                                dbc.Label("3rd Class Fee (LKR) *", style={'fontWeight': '500', 'marginBottom': '8px', 'fontSize': '13px', 'color': COLORS['text_secondary']}),
                                dbc.Input(id="edit-pricing-third-class", type="number", placeholder="0.00", min=0, step=0.01),
                            ], width=4),
                        ]),
                    ]),
                    
                    # Alert for feedback
                    html.Div(id="edit-pricing-alert", style={'marginTop': '20px'})
                ]),
                dbc.ModalFooter([
                    dbc.Button([
                        html.I(className="fas fa-times", style={'marginRight': '8px'}),
                        "Cancel"
                    ], id="cancel-edit-pricing-btn", color="secondary", outline=True, style={'padding': '8px 24px'}),
                    dbc.Button([
                        html.I(className="fas fa-save", style={'marginRight': '8px'}),
                        "Save Changes"
                    ], id="save-edit-pricing-btn", style={**BUTTON_PRIMARY, 'padding': '8px 24px'}),
                ], style={'padding': '16px 24px'})
            ], id="edit-pricing-modal", size="lg", is_open=False),

            # Hidden stores for state management
            dcc.Store(id="pricing-edit-id"),
        ], style={'padding': '30px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
