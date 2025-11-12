"""
TCDAFS - Train Schedules Management Page
Manage daily train schedules and timetables
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from components.common.topbar import create_topbar
from config.styles import COLORS, BUTTON_PRIMARY


def train_schedules_layout():
    """
    Create train schedules management page

    Returns:
        Dash HTML component for the schedules page
    """
    return html.Div([
        create_topbar(),
        
        # Add Schedule Modal
        dbc.Modal([
            dbc.ModalHeader([
                html.Div([
                    html.I(className="fas fa-calendar-plus", style={
                        'fontSize': '24px',
                        'color': COLORS['primary'],
                        'marginRight': '12px'
                    }),
                    dbc.ModalTitle("Add New Train Schedule", style={
                        'fontSize': '22px',
                        'fontWeight': '700',
                        'color': COLORS['text_primary']
                    })
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], style={'borderBottom': f'2px solid {COLORS["border"]}', 'padding': '20px 24px'}),
            
            dbc.ModalBody([
                dbc.Alert(id="add-schedule-modal-alert", is_open=False, duration=4000),
                
                # Section 1: Basic Information
                html.Div([
                    html.H6([
                        html.I(className="fas fa-info-circle", style={'marginRight': '8px', 'color': COLORS['primary']}),
                        "Basic Information"
                    ], style={
                        'color': COLORS['primary'],
                        'fontWeight': '700',
                        'marginBottom': '16px',
                        'fontSize': '16px',
                        'borderBottom': f'2px solid {COLORS["primary"]}20',
                        'paddingBottom': '8px'
                    }),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-hashtag", style={'marginRight': '6px', 'fontSize': '11px'}),
                                "Schedule ID"
                            ], style={'fontWeight': '600', 'fontSize': '13px', 'color': COLORS['text_secondary'], 'marginBottom': '8px'}),
                            dbc.Input(
                                id="add-schedule-id",
                                placeholder="Auto-generated...",
                                disabled=True,
                                style={
                                    'marginBottom': '16px',
                                    'backgroundColor': '#f8f9fa',
                                    'border': f'1px solid {COLORS["border"]}',
                                    'fontSize': '14px',
                                    'fontWeight': '600',
                                    'color': COLORS['primary']
                                }
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-route", style={'marginRight': '6px', 'fontSize': '11px'}),
                                "Route ID *"
                            ], style={'fontWeight': '600', 'fontSize': '13px', 'color': COLORS['text_secondary'], 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="add-schedule-route",
                                placeholder="Select route...",
                                searchable=True,
                                style={'marginBottom': '16px'}
                            ),
                        ], width=6),
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-tag", style={'marginRight': '6px', 'fontSize': '11px'}),
                                "Schedule Name"
                            ], style={'fontWeight': '600', 'fontSize': '13px', 'color': COLORS['text_secondary'], 'marginBottom': '8px'}),
                            dbc.Input(
                                id="add-schedule-name",
                                placeholder="Auto-generated from stations...",
                                disabled=True,
                                style={
                                    'marginBottom': '16px',
                                    'backgroundColor': '#f8f9fa',
                                    'border': f'1px solid {COLORS["border"]}',
                                    'fontSize': '14px',
                                    'fontWeight': '500'
                                }
                            ),
                        ], width=12),
                    ]),
                ], style={
                    'padding': '20px',
                    'backgroundColor': '#fafbfc',
                    'borderRadius': '12px',
                    'marginBottom': '24px',
                    'border': f'1px solid {COLORS["border"]}'
                }),
                
                # Section 2: Station & Timing
                html.Div([
                    html.H6([
                        html.I(className="fas fa-map-marked-alt", style={'marginRight': '8px', 'color': COLORS['primary']}),
                        "Station & Timing Details"
                    ], style={
                        'color': COLORS['primary'],
                        'fontWeight': '700',
                        'marginBottom': '16px',
                        'fontSize': '16px',
                        'borderBottom': f'2px solid {COLORS["primary"]}20',
                        'paddingBottom': '8px'
                    }),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-map-marker-alt", style={'marginRight': '6px', 'fontSize': '11px', 'color': '#059669'}),
                                "Origin Station *"
                            ], style={'fontWeight': '600', 'fontSize': '13px', 'color': COLORS['text_secondary'], 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="add-schedule-origin-station",
                                placeholder="Select departure station...",
                                searchable=True,
                                style={'marginBottom': '16px'}
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-clock", style={'marginRight': '6px', 'fontSize': '11px'}),
                                "Departure Time *"
                            ], style={'fontWeight': '600', 'fontSize': '13px', 'color': COLORS['text_secondary'], 'marginBottom': '8px'}),
                            dbc.Input(
                                id="add-schedule-origin-time",
                                type="time",
                                style={
                                    'marginBottom': '16px',
                                    'fontSize': '14px',
                                    'fontWeight': '500'
                                }
                            ),
                        ], width=6),
                    ]),
                    
                    html.Div([
                        html.I(className="fas fa-arrow-down", style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '20px'
                        })
                    ], style={'textAlign': 'center', 'margin': '8px 0'}),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-map-marker-alt", style={'marginRight': '6px', 'fontSize': '11px', 'color': '#dc2626'}),
                                "Destination Station *"
                            ], style={'fontWeight': '600', 'fontSize': '13px', 'color': COLORS['text_secondary'], 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="add-schedule-destination-station",
                                placeholder="Select arrival station...",
                                searchable=True,
                                style={'marginBottom': '16px'}
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-clock", style={'marginRight': '6px', 'fontSize': '11px'}),
                                "Arrival Time *"
                            ], style={'fontWeight': '600', 'fontSize': '13px', 'color': COLORS['text_secondary'], 'marginBottom': '8px'}),
                            dbc.Input(
                                id="add-schedule-destination-time",
                                type="time",
                                style={
                                    'marginBottom': '16px',
                                    'fontSize': '14px',
                                    'fontWeight': '500'
                                }
                            ),
                        ], width=6),
                    ]),
                ], style={
                    'padding': '20px',
                    'backgroundColor': '#fafbfc',
                    'borderRadius': '12px',
                    'marginBottom': '24px',
                    'border': f'1px solid {COLORS["border"]}'
                }),
                
                # Section 3: Operating Schedule
                html.Div([
                    html.H6([
                        html.I(className="fas fa-calendar-week", style={'marginRight': '8px', 'color': COLORS['primary']}),
                        "Operating Schedule *"
                    ], style={
                        'color': COLORS['primary'],
                        'fontWeight': '700',
                        'marginBottom': '16px',
                        'fontSize': '16px',
                        'borderBottom': f'2px solid {COLORS["primary"]}20',
                        'paddingBottom': '8px'
                    }),
                    
                    html.Div([
                        html.Label("Regular Days", style={
                            'fontWeight': '600',
                            'fontSize': '13px',
                            'color': COLORS['text_secondary'],
                            'marginBottom': '12px',
                            'display': 'block'
                        }),
                        dbc.Checklist(
                            id="add-schedule-weekdays",
                            options=[
                                {"label": html.Div([
                                    html.I(className="fas fa-calendar-day", style={'marginRight': '6px', 'fontSize': '12px'}),
                                    "Monday"
                                ], style={'display': 'inline-flex', 'alignItems': 'center'}), "value": "monday"},
                                {"label": html.Div([
                                    html.I(className="fas fa-calendar-day", style={'marginRight': '6px', 'fontSize': '12px'}),
                                    "Tuesday"
                                ], style={'display': 'inline-flex', 'alignItems': 'center'}), "value": "tuesday"},
                                {"label": html.Div([
                                    html.I(className="fas fa-calendar-day", style={'marginRight': '6px', 'fontSize': '12px'}),
                                    "Wednesday"
                                ], style={'display': 'inline-flex', 'alignItems': 'center'}), "value": "wednesday"},
                                {"label": html.Div([
                                    html.I(className="fas fa-calendar-day", style={'marginRight': '6px', 'fontSize': '12px'}),
                                    "Thursday"
                                ], style={'display': 'inline-flex', 'alignItems': 'center'}), "value": "thursday"},
                                {"label": html.Div([
                                    html.I(className="fas fa-calendar-day", style={'marginRight': '6px', 'fontSize': '12px'}),
                                    "Friday"
                                ], style={'display': 'inline-flex', 'alignItems': 'center'}), "value": "friday"},
                                {"label": html.Div([
                                    html.I(className="fas fa-calendar-day", style={'marginRight': '6px', 'fontSize': '12px'}),
                                    "Saturday"
                                ], style={'display': 'inline-flex', 'alignItems': 'center'}), "value": "saturday"},
                                {"label": html.Div([
                                    html.I(className="fas fa-calendar-day", style={'marginRight': '6px', 'fontSize': '12px'}),
                                    "Sunday"
                                ], style={'display': 'inline-flex', 'alignItems': 'center'}), "value": "sunday"},
                            ],
                            value=[],
                            inline=True,
                            style={'marginBottom': '20px'},
                            className="custom-checklist"
                        ),
                    ]),
                    
                    html.Div([
                        html.Label("Special Days", style={
                            'fontWeight': '600',
                            'fontSize': '13px',
                            'color': COLORS['text_secondary'],
                            'marginBottom': '12px',
                            'display': 'block'
                        }),
                        dbc.Checklist(
                            id="add-schedule-special-days",
                            options=[
                                {"label": html.Div([
                                    html.I(className="fas fa-moon", style={'marginRight': '6px', 'fontSize': '12px', 'color': '#f59e0b'}),
                                    "Poya Day"
                                ], style={'display': 'inline-flex', 'alignItems': 'center'}), "value": "poya_day"},
                                {"label": html.Div([
                                    html.I(className="fas fa-calendar-check", style={'marginRight': '6px', 'fontSize': '12px', 'color': COLORS['primary']}),
                                    "Public Holiday"
                                ], style={'display': 'inline-flex', 'alignItems': 'center'}), "value": "holiday"},
                            ],
                            value=[],
                            inline=True,
                            className="custom-checklist"
                        ),
                    ]),
                ], style={
                    'padding': '20px',
                    'backgroundColor': '#fafbfc',
                    'borderRadius': '12px',
                    'marginBottom': '24px',
                    'border': f'1px solid {COLORS["border"]}'
                }),
                
                # Section 4: Status
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-toggle-on", style={'marginRight': '6px', 'fontSize': '11px'}),
                                "Initial Status *"
                            ], style={'fontWeight': '600', 'fontSize': '13px', 'color': COLORS['text_secondary'], 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="add-schedule-status",
                                options=[
                                    {"label": html.Div([
                                        html.I(className="fas fa-check-circle", style={'marginRight': '8px', 'color': '#059669'}),
                                        "Active"
                                    ], style={'display': 'flex', 'alignItems': 'center'}), "value": "Active"},
                                    {"label": html.Div([
                                        html.I(className="fas fa-times-circle", style={'marginRight': '8px', 'color': '#dc2626'}),
                                        "Inactive"
                                    ], style={'display': 'flex', 'alignItems': 'center'}), "value": "Inactive"},
                                ],
                                value="Active",
                                clearable=False,
                                style={'fontSize': '14px'}
                            ),
                        ], width=6),
                    ]),
                ], style={
                    'padding': '20px',
                    'backgroundColor': '#fafbfc',
                    'borderRadius': '12px',
                    'border': f'1px solid {COLORS["border"]}'
                }),
            ], style={'padding': '24px', 'maxHeight': '70vh', 'overflowY': 'auto'}),
            
            dbc.ModalFooter([
                dbc.Button([
                    html.I(className="fas fa-times", style={'marginRight': '8px'}),
                    "Cancel"
                ], id="close-add-schedule-modal", color="light", outline=True, style={
                    'fontWeight': '600',
                    'padding': '10px 24px',
                    'borderRadius': '8px',
                    'fontSize': '14px'
                }),
                dbc.Button([
                    html.I(className="fas fa-check", style={'marginRight': '8px'}),
                    "Create Schedule"
                ], id="save-add-schedule-btn", color="primary", style={
                    'fontWeight': '600',
                    'padding': '10px 24px',
                    'borderRadius': '8px',
                    'fontSize': '14px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
                }),
            ], style={'borderTop': f'2px solid {COLORS["border"]}', 'padding': '16px 24px'}),
        ], id="add-schedule-modal", is_open=False, size="xl", backdrop="static", scrollable=True),
        
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.I(className="fas fa-calendar-alt", style={
                        'fontSize': '32px',
                        'color': COLORS['primary'],
                        'marginRight': '16px'
                    }),
                    html.Div([
                        html.H3("Train Schedules Management", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '28px'
                        }),
                        html.P("Manage daily train schedules and timetables", style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '14px',
                            'margin': '4px 0 0 0'
                        })
                    ])
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '0'}),
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-plus", style={'marginRight': '8px'}),
                        "Add New Schedule"
                    ], id="add-train-schedule-btn", style=BUTTON_PRIMARY)
                ], style={'marginLeft': 'auto'})
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'background': f'linear-gradient(135deg, {COLORS["surface"]} 0%, #f8f9fa 100%)',
                'padding': '24px 30px',
                'marginBottom': '30px',
                'borderRadius': '16px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.06)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Alert for CRUD operations
            dbc.Alert(id="train-schedule-alert", is_open=False, duration=4000, style={'marginBottom': '20px'}),

            # Filter Section
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-filter", style={
                            'marginRight': '12px',
                            'color': COLORS['primary'],
                            'fontSize': '20px'
                        }),
                        html.H5("Filter Schedules", style={
                            'display': 'inline',
                            'margin': '0',
                            'fontWeight': '700',
                            'color': COLORS['text_primary']
                        })
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    html.P("Narrow down schedules by date and stations", style={
                        'margin': '8px 0 0 32px',
                        'fontSize': '13px',
                        'color': COLORS['text_secondary']
                    })
                ], style={
                    'padding': '20px 24px',
                    'borderBottom': f'2px solid {COLORS["border"]}',
                    'background': 'linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%)'
                }),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-calendar", style={'marginRight': '8px', 'fontSize': '12px'}),
                                "Schedule Date"
                            ], style={
                                'fontWeight': '600',
                                'marginBottom': '10px',
                                'fontSize': '13px',
                                'color': COLORS['text_secondary']
                            }),
                            dbc.Input(
                                id="filter-train-schedule-date",
                                type="date",
                                value=datetime.now().strftime("%Y-%m-%d"),
                                style={
                                    'borderRadius': '8px',
                                    'border': f'1.5px solid {COLORS["border"]}',
                                    'fontSize': '14px',
                                    'padding': '10px 14px'
                                }
                            ),
                        ], width=4),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-map-marker-alt", style={
                                    'marginRight': '8px',
                                    'fontSize': '12px',
                                    'color': '#059669'
                                }),
                                "Origin Station"
                            ], style={
                                'fontWeight': '600',
                                'marginBottom': '10px',
                                'fontSize': '13px',
                                'color': COLORS['text_secondary']
                            }),
                            dcc.Dropdown(
                                id="filter-train-schedule-origin",
                                placeholder="Select departure station...",
                                clearable=True,
                                searchable=True
                            ),
                        ], width=4),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-map-marker-alt", style={
                                    'marginRight': '8px',
                                    'fontSize': '12px',
                                    'color': '#dc2626'
                                }),
                                "Destination Station"
                            ], style={
                                'fontWeight': '600',
                                'marginBottom': '10px',
                                'fontSize': '13px',
                                'color': COLORS['text_secondary']
                            }),
                            dcc.Dropdown(
                                id="filter-train-schedule-destination",
                                placeholder="Select arrival station...",
                                clearable=True,
                                searchable=True
                            ),
                        ], width=4),
                    ], style={'marginBottom': '20px'}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-search", style={'marginRight': '10px'}),
                                "Apply Filters"
                            ], id="apply-train-schedule-filter", color="primary", style={
                                'width': '100%',
                                'padding': '12px 24px',
                                'fontWeight': '600',
                                'borderRadius': '8px',
                                'fontSize': '14px'
                            })
                        ], width=4),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-redo", style={'marginRight': '10px'}),
                                "Clear Filters"
                            ], id="clear-train-schedule-filters", color="light", outline=True, style={
                                'width': '100%',
                                'padding': '12px 24px',
                                'fontWeight': '600',
                                'borderRadius': '8px',
                                'fontSize': '14px',
                                'border': f'2px solid {COLORS["border"]}',
                                'color': '#000000'
                            })
                        ], width=4),
                    ])
                ], style={'padding': '24px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 6px 20px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}',
                'marginBottom': '30px'
            }),

            # Train Schedules Table
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-list-alt", style={
                            'marginRight': '12px',
                            'color': COLORS['primary'],
                            'fontSize': '20px'
                        }),
                        html.H5("All Train Schedules", style={
                            'display': 'inline',
                            'margin': '0',
                            'fontWeight': '700',
                            'color': COLORS['text_primary']
                        })
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    html.Span(id="schedule-count-badge", style={
                        'marginLeft': 'auto',
                        'background': 'linear-gradient(135deg, #C41E3A 0%, #9B1829 100%)',
                        'color': 'white',
                        'padding': '6px 16px',
                        'borderRadius': '20px',
                        'fontSize': '13px',
                        'fontWeight': '700'
                    })
                ], style={
                    'padding': '20px 24px',
                    'borderBottom': f'2px solid {COLORS["border"]}',
                    'background': 'linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%)',
                    'display': 'flex',
                    'alignItems': 'center'
                }),
                html.Div([
                    html.Div(id="train-schedules-table", style={'minHeight': '300px'})
                ], style={'padding': '24px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 6px 20px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Add/Edit Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="train-schedule-modal-title")),
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Train *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(id="train-schedule-train", placeholder="Select train..."),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Route *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(id="train-schedule-route", placeholder="Select route..."),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Schedule Date *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(id="train-schedule-date", type="date"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Departure Time *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(id="train-schedule-departure", type="time"),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Arrival Time *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(id="train-schedule-arrival", type="time"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Status *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="train-schedule-status",
                                options=[
                                    {"label": "Scheduled", "value": "Scheduled"},
                                    {"label": "In Progress", "value": "In Progress"},
                                    {"label": "Completed", "value": "Completed"},
                                    {"label": "Cancelled", "value": "Cancelled"},
                                    {"label": "Delayed", "value": "Delayed"}
                                ],
                                value="Scheduled"
                            ),
                        ], width=6),
                    ]),
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-train-schedule-btn", color="secondary", outline=True),
                    dbc.Button("Save", id="save-train-schedule-btn", style=BUTTON_PRIMARY),
                ])
            ], id="train-schedule-modal", size="lg", is_open=False),

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
                    html.P("Are you sure you want to delete this schedule?", style={
                        'textAlign': 'center',
                        'fontSize': '16px',
                        'marginBottom': '8px'
                    }),
                    html.P(id="train-schedule-delete-name", style={
                        'textAlign': 'center',
                        'fontWeight': '600',
                        'color': COLORS['primary'],
                        'fontSize': '18px'
                    })
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-delete-train-schedule-btn", color="secondary", outline=True),
                    dbc.Button("Delete", id="confirm-delete-train-schedule-btn", color="danger"),
                ])
            ], id="train-schedule-delete-modal", is_open=False),

            # Hidden stores for state management
            dcc.Store(id="train-schedule-edit-id"),
            dcc.Store(id="train-schedule-delete-id"),
        ], style={'padding': '30px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
