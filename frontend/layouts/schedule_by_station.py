"""
TCDAFS - Schedule by Station Search Page
Search train schedules by origin and destination stations
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from components.common.topbar import create_topbar
from config.styles import COLORS, BUTTON_PRIMARY


def schedule_by_station_layout():
    """
    Create schedule by station search page

    Returns:
        Dash HTML component for the schedule by station search page
    """
    return html.Div([
        create_topbar(),
        
        # Edit Time Modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Edit Schedule Times")),
            dbc.ModalBody([
                dbc.Alert(id="edit-time-alert", is_open=False, duration=4000),
                html.Div(id="edit-time-schedule-info", style={'marginBottom': '20px'}),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Origin Departure Time *", style={'fontWeight': '600', 'marginBottom': '8px'}),
                        dbc.Input(
                            id="edit-origin-departure",
                            type="time",
                            style={'marginBottom': '16px'}
                        ),
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Destination Arrival Time *", style={'fontWeight': '600', 'marginBottom': '8px'}),
                        dbc.Input(
                            id="edit-destination-arrival",
                            type="time",
                            style={'marginBottom': '16px'}
                        ),
                    ], width=6),
                ]),
                html.Div(id="edit-segment-id", style={'display': 'none'}),  # Hidden field to store segment ID
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="close-edit-time-modal", color="secondary", outline=True),
                dbc.Button([
                    html.I(className="fas fa-save", style={'marginRight': '8px'}),
                    "Save Changes"
                ], id="save-edit-time-btn", color="primary"),
            ])
        ], id="edit-time-modal", is_open=False, backdrop="static"),
        
        html.Div([
            html.H4("Schedule by Station", style={
                'color': COLORS['text_primary'],
                'fontWeight': '700',
                'marginBottom': '24px'
            }),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("Search Train Schedules", style={
                            'padding': '20px',
                            'borderBottom': f'1px solid {COLORS["border"]}',
                            'margin': '0'
                        }),
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Origin Station *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                                    dcc.Dropdown(
                                        id="schedule-origin-station",
                                        placeholder="Select origin station...",
                                        searchable=True,
                                        clearable=True,
                                        style={'marginBottom': '16px'}
                                    ),
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Destination Station", style={'fontWeight': '500', 'marginBottom': '8px'}),
                                    dcc.Dropdown(
                                        id="schedule-destination-station",
                                        placeholder="Select destination station (optional)...",
                                        searchable=True,
                                        clearable=True,
                                        style={'marginBottom': '16px'}
                                    ),
                                ], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Select Date", style={'fontWeight': '500', 'marginBottom': '8px'}),
                                    dbc.Input(
                                        id="schedule-date-picker",
                                        type="date",
                                        value=datetime.now().strftime("%Y-%m-%d"),
                                        style={'marginBottom': '16px'}
                                    ),
                                ], width=6),
                                dbc.Col([
                                    html.Div([
                                        dbc.Button([
                                            html.I(className="fas fa-search", style={'marginRight': '8px'}),
                                            "Search Schedules"
                                        ], id="search-schedules-btn", style={
                                            **BUTTON_PRIMARY,
                                            'marginTop': '28px',
                                            'width': '100%'
                                        })
                                    ])
                                ], width=6),
                            ]),
                            dbc.Alert(id="schedule-station-alert", is_open=False, duration=4000, style={'marginTop': '16px'}),
                        ], style={'padding': '20px'})
                    ], style={
                        'background': COLORS['surface'],
                        'borderRadius': '12px',
                        'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                        'border': f'1px solid {COLORS["border"]}',
                        'marginBottom': '24px'
                    })
                ], width=12),
            ]),
            # Results display
            html.Div(id="schedule-results-container", style={'marginTop': '24px'})
        ], style={'padding': '30px'})
    ])
