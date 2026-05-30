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
            # Enhanced Header with gradient and stats
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-calendar-alt", style={
                                'fontSize': '48px',
                                'color': COLORS['primary'],
                                'marginBottom': '8px'
                            }),
                        ], style={
                            'width': '80px',
                            'height': '80px',
                            'background': f'linear-gradient(135deg, {COLORS["primary"]}15, {COLORS["primary"]}05)',
                            'borderRadius': '20px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginRight': '24px',
                            'boxShadow': f'0 8px 16px {COLORS["primary"]}20'
                        }),
                        html.Div([
                            html.H2("Daily Train Operations", style={
                                'color': COLORS['text_primary'],
                                'fontWeight': '800',
                                'margin': '0',
                                'fontSize': '32px',
                                'letterSpacing': '-0.5px'
                            }),
                            html.P("Monitor scheduled services, track real-time operations, and leverage AI-powered capacity predictions", style={
                                'color': COLORS['text_secondary'],
                                'fontSize': '15px',
                                'margin': '8px 0 0 0',
                                'lineHeight': '1.6',
                                'maxWidth': '600px'
                            })
                        ])
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1'})
            ], style={
                'background': f'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
                'padding': '36px 40px',
                'marginBottom': '32px',
                'borderRadius': '20px',
                'boxShadow': '0 4px 20px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between'
            }),

            # Alert for operations
            dbc.Alert(id="daily-schedule-alert", is_open=False, duration=4000, style={
                'marginBottom': '24px',
                'borderRadius': '12px',
                'border': 'none',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
            }),

            # Advanced Filters Panel
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-sliders-h", style={
                            'marginRight': '12px',
                            'color': COLORS['primary'],
                            'fontSize': '18px'
                        }),
                        html.H5("Smart Filters", style={
                            'display': 'inline',
                            'margin': '0',
                            'fontWeight': '700',
                            'fontSize': '18px',
                            'color': COLORS['text_primary']
                        })
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    html.P("Refine your search using date, route, and schedule parameters", style={
                        'margin': '4px 0 0 30px',
                        'fontSize': '13px',
                        'color': COLORS['text_secondary']
                    })
                ], style={
                    'padding': '24px 28px 20px 28px',
                    'borderBottom': f'2px solid {COLORS["border"]}',
                    'background': 'linear-gradient(to bottom, #fafbfc, #ffffff)'
                }),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-calendar-check", style={'marginRight': '6px'}),
                                "Operating Date"
                            ], style={
                                'fontWeight': '600',
                                'marginBottom': '10px',
                                'fontSize': '14px',
                                'color': COLORS['text_primary']
                            }),
                            dbc.Input(
                                id="daily-schedule-date",
                                type="date",
                                value=datetime.now().strftime("%Y-%m-%d"),
                                style={
                                    'borderRadius': '10px',
                                    'border': f'2px solid {COLORS["border"]}',
                                    'padding': '10px 14px',
                                    'fontSize': '14px',
                                    'fontWeight': '500'
                                }
                            ),
                            dbc.FormText("Select the date to view scheduled operations", color="muted")
                        ], md=3),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-route", style={'marginRight': '6px'}),
                                "Route Filter"
                            ], style={
                                'fontWeight': '600',
                                'marginBottom': '10px',
                                'fontSize': '14px',
                                'color': COLORS['text_primary']
                            }),
                            dcc.Dropdown(
                                id="daily-schedule-route-filter",
                                placeholder="Filter by route (optional)",
                                clearable=True,
                                searchable=True,
                                style={'fontSize': '14px'}
                            ),
                            dbc.FormText("Search and select a specific route", color="muted")
                        ], md=4),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-barcode", style={'marginRight': '6px'}),
                                "Schedule ID"
                            ], style={
                                'fontWeight': '600',
                                'marginBottom': '10px',
                                'fontSize': '14px',
                                'color': COLORS['text_primary']
                            }),
                            dbc.Input(
                                id="daily-schedule-id-filter",
                                type="text",
                                placeholder="Enter schedule ID (e.g., TS001)",
                                style={
                                    'borderRadius': '10px',
                                    'border': f'2px solid {COLORS["border"]}',
                                    'padding': '10px 14px',
                                    'fontSize': '14px'
                                }
                            ),
                            dbc.FormText("Filter by specific schedule identifier", color="muted")
                        ], md=3),
                        dbc.Col([
                            dbc.Label("\u00A0", style={'marginBottom': '10px', 'display': 'block'}),
                            dbc.Button([
                                html.I(className="fas fa-search", style={'marginRight': '10px'}),
                                "Search Schedules"
                            ], id="load-daily-schedules-btn", style={
                                **BUTTON_PRIMARY,
                                'width': '100%',
                                'padding': '12px 20px',
                                'fontSize': '14px',
                                'fontWeight': '700',
                                'borderRadius': '10px',
                                'boxShadow': f'0 4px 12px {COLORS["primary"]}30'
                            })
                        ], md=2),
                    ], className="g-3")
                ], style={'padding': '28px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 20px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}',
                'marginBottom': '28px'
            }),

            # Schedules Results Panel
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-train", style={
                                'marginRight': '12px',
                                'color': COLORS['primary'],
                                'fontSize': '20px'
                            }),
                            html.H5("Scheduled Services", style={
                                'display': 'inline',
                                'margin': '0',
                                'fontWeight': '700',
                                'fontSize': '18px'
                            })
                        ], style={'display': 'flex', 'alignItems': 'center'}),
                        html.Span(id="daily-schedule-count", style={
                            'padding': '6px 16px',
                            'background': f'linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary"]}dd)',
                            'color': 'white',
                            'borderRadius': '20px',
                            'fontSize': '14px',
                            'fontWeight': '700',
                            'boxShadow': f'0 4px 12px {COLORS["primary"]}40',
                            'letterSpacing': '0.5px'
                        })
                    ], style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'space-between'
                    }),
                    html.P("AI-powered predictions available for optimized compartment allocation", style={
                        'margin': '8px 0 0 32px',
                        'fontSize': '13px',
                        'color': COLORS['text_secondary']
                    })
                ], style={
                    'padding': '24px 28px 20px 28px',
                    'borderBottom': f'2px solid {COLORS["border"]}',
                    'background': 'linear-gradient(to bottom, #fafbfc, #ffffff)'
                }),
                html.Div([
                    html.Div(id="daily-schedules-container", style={'minHeight': '450px'})
                ], style={'padding': '24px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 20px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Status Update Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle([
                    html.I(className="fas fa-edit", style={'marginRight': '10px'}),
                    "Update Schedule Status"
                ]), close_button=True),
                dbc.ModalBody([
                    html.Div(id="status-update-schedule-info", style={'marginBottom': '20px'}),
                    dbc.Label("New Status *", style={'fontWeight': '600', 'marginBottom': '10px'}),
                    dcc.Dropdown(
                        id="daily-schedule-new-status",
                        options=[
                            {"label": "🕐 Scheduled", "value": "Scheduled"},
                            {"label": "🚂 In Progress", "value": "In Progress"},
                            {"label": "✅ Completed", "value": "Completed"},
                            {"label": "❌ Cancelled", "value": "Cancelled"},
                            {"label": "⏰ Delayed", "value": "Delayed"}
                        ],
                        placeholder="Select new status..."
                    ),
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-status-update-btn", color="secondary", outline=True, style={
                        'borderRadius': '8px',
                        'padding': '8px 20px',
                        'fontWeight': '600'
                    }),
                    dbc.Button("Update Status", id="confirm-status-update-btn", style={
                        **BUTTON_PRIMARY,
                        'borderRadius': '8px',
                        'padding': '8px 20px',
                        'fontWeight': '600'
                    }),
                ])
            ], id="status-update-modal", is_open=False),

            # Hidden store for schedule ID
            dcc.Store(id="daily-schedule-update-id"),
        ], style={'padding': '32px 36px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
