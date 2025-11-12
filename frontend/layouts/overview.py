"""
TCDAFS - Overview Dashboard Page
Main dashboard with statistics, charts, and KPIs
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.common.topbar import create_topbar
from config.styles import COLORS


def overview_layout():
    """
    Create dashboard overview page with stats and charts

    Returns:
        Dash HTML component for the overview page
    """
    return html.Div([
        create_topbar(),
        html.Div([
            # Header with gradient background
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-line", style={
                        'fontSize': '36px',
                        'color': COLORS['primary'],
                        'marginRight': '20px'
                    }),
                    html.Div([
                        html.H3("Executive Dashboard", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '32px',
                            'letterSpacing': '-0.5px'
                        }),
                        html.P("Comprehensive real-time analytics and key performance indicators for railway operations", style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '15px',
                            'margin': '8px 0 0 0',
                            'lineHeight': '1.5'
                        })
                    ])
                ], style={
                    'display': 'flex',
                    'alignItems': 'center'
                })
            ], style={
                'background': f'linear-gradient(135deg, {COLORS["surface"]} 0%, #f8f9fa 100%)',
                'padding': '28px 32px',
                'marginBottom': '32px',
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # KPI Cards Row with improved styling
            dbc.Row([
                dbc.Col(html.Div(id="stat-card-1"), width=3),
                dbc.Col(html.Div(id="stat-card-2"), width=3),
                dbc.Col(html.Div(id="stat-card-3"), width=3),
                dbc.Col(html.Div(id="stat-card-4"), width=3),
            ], className="mb-4"),

            # Charts Section with improved layout
            dbc.Row([
                # Daily Ticket Sales Chart - Full width with enhanced styling
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-chart-area", style={
                                    'color': COLORS['primary'],
                                    'marginRight': '12px',
                                    'fontSize': '22px'
                                }),
                                html.H5("Ticket Sales Performance", style={
                                    'color': COLORS['text_primary'],
                                    'fontWeight': '600',
                                    'margin': '0',
                                    'display': 'inline',
                                    'fontSize': '19px'
                                }),
                            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'}),
                            html.P("30-day trend analysis of daily ticket bookings and revenue performance metrics", style={
                                'color': COLORS['text_secondary'],
                                'fontSize': '13px',
                                'margin': '0',
                                'lineHeight': '1.4'
                            })
                        ], style={'padding': '24px 24px 16px 24px'}),
                        html.Hr(style={'margin': '0', 'borderColor': COLORS['border'], 'opacity': '0.3'}),
                        dcc.Graph(id="daily-ticket-sales-chart", config={'displayModeBar': False},
                                 style={"height": "350px", "padding": "10px"})
                    ], style={
                        'background': COLORS['surface'],
                        'borderRadius': '16px',
                        'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                        'border': f'1px solid {COLORS["border"]}',
                        'transition': 'all 0.3s ease'
                    }, className="stat-card")
                ], width=12),
            ], className="mb-4"),

            # Pie Charts Row with improved styling
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-calendar-check", style={
                                    'color': COLORS['success'],
                                    'marginRight': '12px',
                                    'fontSize': '20px'
                                }),
                                html.H5("Daily Schedule Completion", style={
                                    'color': COLORS['text_primary'],
                                    'fontWeight': '600',
                                    'margin': '0',
                                    'display': 'inline',
                                    'fontSize': '18px'
                                }),
                            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '6px'}),
                            html.P("Real-time operational status: completed versus pending train schedules", style={
                                'color': COLORS['text_secondary'],
                                'fontSize': '12px',
                                'margin': '0',
                                'lineHeight': '1.4'
                            })
                        ], style={'padding': '20px 20px 12px 20px'}),
                        html.Hr(style={'margin': '0', 'borderColor': COLORS['border'], 'opacity': '0.3'}),
                        dcc.Graph(id="schedule-status-pie", config={'displayModeBar': False},
                                 style={"height": "320px"})
                    ], style={
                        'background': COLORS['surface'],
                        'borderRadius': '16px',
                        'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                        'border': f'1px solid {COLORS["border"]}',
                        'transition': 'all 0.3s ease',
                        'height': '100%'
                    }, className="stat-card")
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-users", style={
                                    'color': COLORS['info'],
                                    'marginRight': '12px',
                                    'fontSize': '20px'
                                }),
                                html.H5("Passenger Class Analytics", style={
                                    'color': COLORS['text_primary'],
                                    'fontWeight': '600',
                                    'margin': '0',
                                    'display': 'inline',
                                    'fontSize': '18px'
                                }),
                            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '6px'}),
                            html.P("Current distribution of bookings across first, second, and third class accommodations", style={
                                'color': COLORS['text_secondary'],
                                'fontSize': '12px',
                                'margin': '0',
                                'lineHeight': '1.4'
                            })
                        ], style={'padding': '20px 20px 12px 20px'}),
                        html.Hr(style={'margin': '0', 'borderColor': COLORS['border'], 'opacity': '0.3'}),
                        dcc.Graph(id="class-distribution-pie", config={'displayModeBar': False},
                                 style={"height": "320px"})
                    ], style={
                        'background': COLORS['surface'],
                        'borderRadius': '16px',
                        'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                        'border': f'1px solid {COLORS["border"]}',
                        'transition': 'all 0.3s ease',
                        'height': '100%'
                    }, className="stat-card")
                ], width=6),
            ]),
            dcc.Interval(id="overview-interval", interval=10000, n_intervals=0)
        ], style={'padding': '30px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
