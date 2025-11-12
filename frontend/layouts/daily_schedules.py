"""
TCDAFS - Daily Schedules Page
View and manage running schedules by date
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from components.common.topbar import create_topbar
from config.styles import COLORS, BUTTON_PRIMARY


def daily_schedules_layout():
    """
    Create daily schedules page

    Returns:
        Dash HTML component for the daily schedules page
    """
    return html.Div([
        create_topbar(),
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.I(className="fas fa-calendar-day", style={
                        'fontSize': '32px',
                        'color': COLORS['primary'],
                        'marginRight': '16px'
                    }),
                    html.Div([
                        html.H3("Daily Schedules", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '28px'
                        }),
                        html.P("View running schedules and generate AI predictions", style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '14px',
                            'margin': '4px 0 0 0'
                        })
                    ])
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], style={
                'background': f'linear-gradient(135deg, {COLORS["surface"]} 0%, #f8f9fa 100%)',
                'padding': '24px 30px',
                'marginBottom': '30px',
                'borderRadius': '16px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.06)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Alert for operations
            dbc.Alert(id="daily-schedule-alert", is_open=False, duration=4000, style={'marginBottom': '20px'}),

            # Date Selector
            html.Div([
                html.Div([
                    html.I(className="fas fa-calendar", style={'marginRight': '10px', 'color': COLORS['primary']}),
                    html.H5("Select Date", style={'display': 'inline', 'margin': '0', 'fontWeight': '600'})
                ], style={'padding': '20px', 'borderBottom': f'1px solid {COLORS["border"]}'}),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Schedule Date *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(
                                id="daily-schedule-date",
                                type="date",
                                value=datetime.now().strftime("%Y-%m-%d"),
                                style={'marginBottom': '0'}
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-search", style={'marginRight': '8px'}),
                                "Load Schedules"
                            ], id="load-daily-schedules-btn", style={**BUTTON_PRIMARY, 'marginTop': '28px', 'width': '100%'})
                        ], width=6),
                    ])
                ], style={'padding': '20px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}',
                'marginBottom': '24px'
            }),

            # Schedules Display
            html.Div([
                html.Div([
                    html.I(className="fas fa-train", style={'marginRight': '10px', 'color': COLORS['primary']}),
                    html.H5("Running Schedules", style={'display': 'inline', 'margin': '0', 'fontWeight': '600'}),
                    html.Span(id="daily-schedule-count", style={
                        'marginLeft': '12px',
                        'padding': '4px 12px',
                        'background': COLORS['primary'],
                        'color': 'white',
                        'borderRadius': '12px',
                        'fontSize': '14px',
                        'fontWeight': '600'
                    })
                ], style={'padding': '20px', 'borderBottom': f'1px solid {COLORS["border"]}'}),
                html.Div([
                    html.Div(id="daily-schedules-container", style={'minHeight': '400px'})
                ], style={'padding': '20px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Status Update Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Update Schedule Status")),
                dbc.ModalBody([
                    html.Div(id="status-update-schedule-info", style={'marginBottom': '20px'}),
                    dbc.Label("New Status *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                    dcc.Dropdown(
                        id="daily-schedule-new-status",
                        options=[
                            {"label": "Scheduled", "value": "Scheduled"},
                            {"label": "In Progress", "value": "In Progress"},
                            {"label": "Completed", "value": "Completed"},
                            {"label": "Cancelled", "value": "Cancelled"},
                            {"label": "Delayed", "value": "Delayed"}
                        ],
                        placeholder="Select new status..."
                    ),
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-status-update-btn", color="secondary", outline=True),
                    dbc.Button("Update Status", id="confirm-status-update-btn", style=BUTTON_PRIMARY),
                ])
            ], id="status-update-modal", is_open=False),

            # Hidden store for schedule ID
            dcc.Store(id="daily-schedule-update-id"),
        ], style={'padding': '30px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
