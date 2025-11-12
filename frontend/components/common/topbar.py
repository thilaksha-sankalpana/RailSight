"""
TCDAFS - Top Navigation Bar Component
Top bar with search, notifications, and profile dropdown
"""
from dash import html
import dash_bootstrap_components as dbc
from config.styles import TOPBAR_STYLE, COLORS


def create_topbar():
    """
    Create top navigation bar with search and user controls

    Returns:
        Dash HTML component for the top navigation bar
    """
    return html.Div([
        # Search Bar
        html.Div([
            html.I(className="fas fa-search", style={
                'position': 'absolute',
                'left': '16px',
                'top': '50%',
                'transform': 'translateY(-50%)',
                'color': COLORS['text_secondary'],
                'fontSize': '16px'
            }),
            dbc.Input(
                id="global-search",
                type="text",
                placeholder="Search schedules, trains, routes...",
                style={
                    'width': '400px',
                    'paddingLeft': '45px',
                    'border': f'2px solid {COLORS["border"]}',
                    'borderRadius': '8px',
                    'transition': 'all 0.3s ease'
                }
            ),
            html.Div(id="search-results", style={
                'position': 'absolute',
                'top': '100%',
                'left': 0,
                'right': 0,
                'background': 'white',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.1)',
                'borderRadius': '8px',
                'marginTop': '8px',
                'maxHeight': '400px',
                'overflowY': 'auto',
                'display': 'none',
                'zIndex': 1000
            })
        ], style={'position': 'relative'}),

        # Right Side Icons
        html.Div([
            # Notifications with improved UI
            html.Div([
                html.Button([
                    html.I(className="fas fa-bell", style={
                        'fontSize': '20px',
                        'color': COLORS['text_primary']
                    }),
                    html.Span("3", className="notification-badge", style={
                        'position': 'absolute',
                        'top': '-2px',
                        'right': '-2px',
                        'background': COLORS['error'],
                        'color': 'white',
                        'borderRadius': '50%',
                        'width': '20px',
                        'height': '20px',
                        'fontSize': '11px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'fontWeight': '700',
                        'border': '2px solid white'
                    })
                ], id="notification-btn", style={
                    'position': 'relative',
                    'background': '#f5f7fa',
                    'border': 'none',
                    'cursor': 'pointer',
                    'padding': '12px',
                    'marginRight': '16px',
                    'borderRadius': '12px',
                    'transition': 'all 0.3s ease',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'width': '44px',
                    'height': '44px'
                }),
                html.Div(id="notification-dropdown", children=[], style={
                    'position': 'absolute',
                    'top': '100%',
                    'right': 0,
                    'width': '350px',
                    'background': 'white',
                    'boxShadow': '0 8px 32px rgba(0,0,0,0.12)',
                    'borderRadius': '16px',
                    'marginTop': '8px',
                    'display': 'none',
                    'zIndex': 1000,
                    'border': f'1px solid {COLORS["border"]}'
                })
            ], style={'position': 'relative'}),

            # User Profile Dropdown with improved UI
            html.Div([
                html.Button([
                    html.I(className="fas fa-user-circle", style={
                        'fontSize': '24px',
                        'color': COLORS['primary']
                    })
                ], id="profile-dropdown-btn", style={
                    'background': '#f5f7fa',
                    'border': f'2px solid {COLORS["border"]}',
                    'cursor': 'pointer',
                    'padding': '10px',
                    'borderRadius': '12px',
                    'transition': 'all 0.3s ease',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'width': '44px',
                    'height': '44px'
                }),
                html.Div([
                    html.Div([
                        html.I(className="fas fa-user-cog", style={
                            'marginRight': '12px',
                            'color': COLORS['primary'],
                            'fontSize': '16px'
                        }),
                        html.Span("Profile Settings")
                    ], id="profile-settings-btn", style={
                        'padding': '12px 16px',
                        'cursor': 'pointer',
                        'transition': 'all 0.2s ease',
                        'borderRadius': '8px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'fontSize': '14px',
                        'fontWeight': '500'
                    }, className="dropdown-menu-item"),
                    html.Div([
                        html.I(className="fas fa-key", style={
                            'marginRight': '12px',
                            'color': COLORS['info'],
                            'fontSize': '16px'
                        }),
                        html.Span("Change Password")
                    ], id="change-password-btn", style={
                        'padding': '12px 16px',
                        'cursor': 'pointer',
                        'transition': 'all 0.2s ease',
                        'borderRadius': '8px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'fontSize': '14px',
                        'fontWeight': '500'
                    }, className="dropdown-menu-item"),
                    html.Hr(style={'margin': '8px 0', 'borderColor': COLORS['border']}),
                    html.Div([
                        html.I(className="fas fa-sign-out-alt", style={
                            'marginRight': '12px',
                            'color': COLORS['error'],
                            'fontSize': '16px'
                        }),
                        html.Span("Logout")
                    ], id="topbar-logout-btn", style={
                        'padding': '12px 16px',
                        'cursor': 'pointer',
                        'transition': 'all 0.2s ease',
                        'borderRadius': '8px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'fontSize': '14px',
                        'fontWeight': '500',
                        'color': COLORS['error']
                    }, className="dropdown-menu-item")
                ], id="profile-dropdown-menu", style={
                    'position': 'absolute',
                    'top': '100%',
                    'right': 0,
                    'width': '220px',
                    'background': 'white',
                    'boxShadow': '0 8px 32px rgba(0,0,0,0.12)',
                    'borderRadius': '16px',
                    'marginTop': '8px',
                    'display': 'none',
                    'zIndex': 1000,
                    'border': f'1px solid {COLORS["border"]}',
                    'padding': '8px'
                })
            ], style={'position': 'relative'})
        ], style={'display': 'flex', 'alignItems': 'center'})
    ], style=TOPBAR_STYLE)
