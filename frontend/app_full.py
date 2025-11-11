# frontend/app_full.py - Version 6.0 (Schema v2.0 Compatible)
"""
TCDAFS - Sri Lanka Railway Professional Dashboard
Updated for Database Schema v2.0 (2025-11-10)
- Separate NIC/Passport fields
- Updated class enums (First/Second/Third)
- Simplified ticket pricing
- Updated field names (schedule_date, operational trains)
"""
import dash
from dash import html, dcc, Input, Output, State, callback, dash_table, no_update
import dash_bootstrap_components as dbc
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
API_URL = "http://localhost:8000"
# Initialize app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    title="TCDAFS - Sri Lanka Railway System"
)
server = app.server
server.secret_key = "srilanka-railway-tcdafs-2025"
# FIXED: Custom favicon with RED train emoji and proper CSS injection
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🚂</text></svg>">
        {%css%}
        <style>
            /* FIXED: Enhanced button hover and click animations */
            button, .btn, a[role="button"] {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            button:hover, .btn:hover, a[role="button"]:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(196, 30, 58, 0.4) !important;
            }
            button:active, .btn:active, a[role="button"]:active {
                transform: translateY(0px) !important;
                box-shadow: 0 2px 8px rgba(196, 30, 58, 0.3) !important;
            }
            /* Login button specific animations */
            #login-button {
                position: relative;
                overflow: hidden;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            #login-button:hover {
                transform: translateY(-3px) !important;
                box-shadow: 0 8px 25px rgba(196, 30, 58, 0.5) !important;
                background: linear-gradient(135deg, 
#E84855 0%, 
#C41E3A 100%) !important;
            }
            #login-button:active {
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 15px rgba(196, 30, 58, 0.4) !important;
            }
            /* Ripple effect */
            #login-button::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: translate(-50%, -50%);
                transition: width 0.6s, height 0.6s;
            }
            #login-button:active::after {
                width: 300px;
                height: 300px;
            }
            /* Navigation link hover effects */
            .nav-link-item {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                position: relative;
            }
            .nav-link-item:hover {
                background: rgba(255, 255, 255, 0.15) !important;
                border-left: 4px solid 
#FFD700 !important;
                transform: translateX(6px);
                color: white !important;
            }
            .nav-link-item:active {
                background: rgba(255, 255, 255, 0.25) !important;
                transform: translateX(8px);
            }
            /* Active nav link - STAYS HIGHLIGHTED */
            .nav-link-active {
                background: rgba(255, 255, 255, 0.2) !important;
                border-left: 4px solid 
#FFD700 !important;
                color: white !important;
                font-weight: 600 !important;
                transform: translateX(4px);
            }
            .nav-link-active:hover {
                background: rgba(255, 255, 255, 0.25) !important;
                transform: translateX(6px);
            }
            /* Input focus animations */
            input:focus, select:focus, textarea:focus, .Select-control:focus {
                transform: scale(1.01);
                box-shadow: 0 0 0 3px rgba(196, 30, 58, 0.1) !important;
                border-color: 
#C41E3A !important;
                transition: all 0.3s ease;
            }
            /* Card hover effects */
            .stat-card {
                transition: all 0.3s ease;
            }
            .stat-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
            }
            /* Dropdown smooth animation - no jump */
            .dropdown-menu {
                animation: smoothSlideDown 0.2s ease-out !important;
                transform-origin: top;
            }
            @keyframes smoothSlideDown {
                from {
                    opacity: 0;
                    transform: translateY(-5px) scaleY(0.95);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scaleY(1);
                }
            }
            @keyframes float {
                0%, 100% {
                    transform: translateY(0px);
                }
                50% {
                    transform: translateY(-20px);
                }
            }
            /* Pulse animation */
            @keyframes pulse {
                0%, 100% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.1);
                }
            }
            .notification-badge {
                animation: pulse 2s ease infinite;
            }
            /* Fade in */
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            .fade-in {
                animation: fadeIn 0.5s ease;
            }
            /* Spinner */
            @keyframes spin {
                to {
                    transform: rotate(360deg);
                }
            }
            .spinner {
                animation: spin 1s linear infinite;
            }
            /* Search bar focus */
            #global-search:focus {
                width: 500px !important;
                transition: width 0.3s ease;
            }
            /* Modal animations */
            .modal-content {
                animation: slideDown 0.3s ease;
            }
            /* User profile hover */
            .user-profile-box:hover {
                background: rgba(255, 255, 255, 0.2) !important;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            /* Ticket card */
            .ticket-card {
                transition: all 0.3s ease;
            }
            .ticket-card:hover {
                transform: translateX(4px);
                box-shadow: -4px 0 12px rgba(196, 30, 58, 0.2);
            }
            /* Schedule card hover */
            .schedule-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12) !important;
            }
            /* Schedule option hover */
            .schedule-option:hover {
                background: #f0f4f8 !important;
                border-color: #C41E3A !important;
            }
            /* Button hover effects */
            button:hover {
                opacity: 0.9;
                transform: scale(1.02);
            }
            /* Top bar icons */
            .top-bar-icon {
                transition: all 0.3s ease;
            }
            .top-bar-icon:hover {
                transform: scale(1.2);
                color: #C41E3A !important;
            }
            /* Gradient background */
            @keyframes gradientShift {
                0% {
                    background-position: 0% 50%;
                }
                50% {
                    background-position: 100% 50%;
                }
                100% {
                    background-position: 0% 50%;
                }
            }
            .animated-gradient {
                background: linear-gradient(135deg, #C41E3A15 0%, #FFD70015 25%, #2196F315 50%, #4CAF5015 75%, #C41E3A15 100%);
                background-size: 400% 400%;
                animation: gradientShift 15s ease infinite;
            }
            /* Logout button */
            #sidebar-logout-btn:hover {
                background: rgba(255, 255, 255, 0.25) !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }
            #sidebar-logout-btn:active {
                transform: translateY(0px);
            }
            /* Dropdown menu items hover */
            .dropdown-menu-item:hover {
                background: #f5f7fa !important;
                transform: translateX(4px);
            }
            /* Notification and profile buttons hover */
            #notification-btn:hover, #profile-dropdown-btn:hover {
                background: #e8ecf1 !important;
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            /* Book ticket button */
            #book-ticket-btn:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 25px rgba(196, 30, 58, 0.5) !important;
            }
            #book-ticket-btn:active {
                transform: translateY(0px) !important;
            }
            /* Ticket count buttons */
            #increase-tickets:hover, #decrease-tickets:hover {
                transform: scale(1.1);
                box-shadow: 0 2px 8px rgba(196, 30, 58, 0.3);
            }
            #increase-tickets:active, #decrease-tickets:active {
                transform: scale(0.95);
            }
            /* Notification button - remove square background */
            #notification-btn {
                background: transparent !important;
                border: none !important;
                padding: 8px !important;
                border-radius: 50% !important;
                transition: all 0.2s ease !important;
            }
            #notification-btn:hover {
                background: rgba(196, 30, 58, 0.1) !important;
                transform: scale(1.1);
            }
            #notification-btn:active {
                transform: scale(0.95);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
# ============= SRI LANKA RAILWAY COLOR SCHEME =============
COLORS = {
    'primary': '#C41E3A',
    'primary_dark': '#9B1829',
    'primary_light': '#E84855',
    'accent': '#FFD700',
    'background': '#F5F5F5',
    'surface': '#FFFFFF',
    'text_primary': '#2C2C2C',
    'text_secondary': '#757575',
    'border': '#E0E0E0',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
    'info': '#2196F3'
}
# ============= STYLES =============
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '280px',
    'padding': '0',
    'background': f'linear-gradient(180deg, {COLORS["primary"]} 0%, {COLORS["primary_dark"]} 100%)',
    'boxShadow': '4px 0 12px rgba(0,0,0,0.15)',
    'zIndex': 1000,
    'overflowY': 'auto',
    'fontFamily': 'Roboto, sans-serif'
}
CONTENT_STYLE = {
    'marginLeft': '280px',
    'padding': '0',
    'background': COLORS['background'],
    'minHeight': '100vh',
    'fontFamily': 'Roboto, sans-serif'
}
TOPBAR_STYLE = {
    'height': '70px',
    'background': COLORS['surface'],
    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
    'padding': '0 30px',
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'space-between',
    'position': 'sticky',
    'top': 0,
    'zIndex': 999
}
# FIXED: Updated nav link style with proper hover state
NAV_LINK_STYLE = {
    'color': 'rgba(255,255,255,0.85)',
    'padding': '16px 24px',
    'marginBottom': '2px',
    'display': 'flex',
    'alignItems': 'center',
    'textDecoration': 'none',
    'transition': 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    'borderLeft': '4px solid transparent',
    'fontSize': '15px',
    'fontWeight': '400',
    'cursor': 'pointer'
}
BUTTON_PRIMARY = {
    'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["primary_dark"]} 100%)',
    'color': 'white',
    'border': 'none',
    'borderRadius': '8px',
    'padding': '12px 24px',
    'fontSize': '15px',
    'fontWeight': '500',
    'cursor': 'pointer',
    'boxShadow': f'0 4px 12px rgba(196, 30, 58, 0.3)',
    'transition': 'all 0.3s ease'
}
# CSS is now in app.index_string for proper loading
# ============= HELPER FUNCTIONS =============
def make_api_request(endpoint, method="GET", token=None, data=None, timeout=10):
    """API request handler with proper error handling"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token.get('access_token', '')}"

        url = f"{API_URL}{endpoint}"

        if method == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method == "PATCH":
            headers["Content-Type"] = "application/json"
            response = requests.patch(url, headers=headers, json=data, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return None

        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"API Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout for {endpoint}")
        return None
    except Exception as e:
        logger.error(f"API request failed: {e}")
        return None
# ============= LOGIN LAYOUT =============
def login_layout():
    return html.Div([
        # No need to inject CSS here - it's in app.index_string

        html.Div([
            html.Div([
                # Logo Section with animation
                html.Div([
                    html.I(className="fas fa-train fa-4x", style={
                        'color': COLORS['primary'],
                        'marginBottom': '20px',
                        'animation': 'float 3s ease-in-out infinite'
                    }),
                ], style={'textAlign': 'center'}),

                html.H2("Sri Lanka Railway", style={
                    'textAlign': 'center',
                    'color': COLORS['text_primary'],
                    'fontWeight': '700',
                    'marginBottom': '8px'
                }),
                html.P("Train Compartment Demand Analysis & Forecasting System", style={
                    'textAlign': 'center',
                    'color': COLORS['text_secondary'],
                    'fontSize': '14px',
                    'marginBottom': '40px'
                }),

                # Alert
                dbc.Alert(id="login-alert", is_open=False, dismissable=True),

                # Login Form
                html.Div([
                    dbc.Label("Email Address", style={'fontWeight': '500', 'marginBottom': '8px'}),
                    dbc.Input(
                        id="login-username",
                        type="email",
                        placeholder="user@railway.lk",
                        className="fade-in",
                        style={'borderRadius': '8px', 'marginBottom': '20px', 'transition': 'all 0.3s ease'}
                    ),
                ]),

                html.Div([
                    dbc.Label("Password", style={'fontWeight': '500', 'marginBottom': '8px'}),
                    dbc.Input(
                        id="login-password",
                        type="password",
                        placeholder="Enter your password",
                        className="fade-in",
                        style={'borderRadius': '8px', 'marginBottom': '32px', 'transition': 'all 0.3s ease'}
                    ),
                ]),

                # FIXED: Login button with enhanced hover and click animations
                dbc.Button([
                    html.I(className="fas fa-sign-in-alt", style={'marginRight': '8px'}),
                    "Sign In"
                ], id="login-button", style={
                    **BUTTON_PRIMARY,
                    'width': '100%',
                    'padding': '14px'
                }),

                # Footer
                html.Div([
                    html.P([
                        html.I(className="fas fa-shield-alt", style={'marginRight': '8px'}),
                        "Secure Login - Railway Officials Only"
                    ], style={
                        'textAlign': 'center',
                        'color': COLORS['text_secondary'],
                        'fontSize': '13px',
                        'marginTop': '24px'
                    })
                ])
            ], style={
                'background': 'white',
                'padding': '48px',
                'borderRadius': '16px',
                'boxShadow': '0 20px 60px rgba(0,0,0,0.15)',
                'maxWidth': '440px',
                'width': '100%',
                'position': 'relative',
                'zIndex': 10
            })
        ], style={
            'minHeight': '100vh',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'padding': '20px',
            'background': 'linear-gradient(135deg, #C41E3A15 0%, #FFD70015 25%, #2196F315 50%, #4CAF5015 75%, #C41E3A15 100%)',
            'backgroundSize': '400% 400%',
            'animation': 'gradientShift 15s ease infinite',
            'position': 'relative'
        })
    ])
# ============= SIDEBAR =============
def create_sidebar(username="User", email="user@railway.lk", full_name="Administrator", current_path="/"):
    nav_items = [
        {'icon': 'fas fa-chart-line', 'label': 'Overview', 'path': '/'},
        {'icon': 'fas fa-ticket-alt', 'label': 'Ticket Booking', 'path': '/tickets'},
        {'icon': 'fas fa-train', 'label': 'Train Models', 'path': '/train-models'},
        {'icon': 'fas fa-subway', 'label': 'Operational Trains', 'path': '/trains'},
        {'icon': 'fas fa-route', 'label': 'Train Routes', 'path': '/routes'},
        {'icon': 'fas fa-calendar-alt', 'label': 'Train Schedules', 'path': '/schedules'},
        {'icon': 'fas fa-map-marker-alt', 'label': 'Schedule by Station', 'path': '/schedule-stations'},
        {'icon': 'fas fa-dollar-sign', 'label': 'Ticket Pricing', 'path': '/pricing'},
        {'icon': 'fas fa-calendar-day', 'label': 'Daily Schedules', 'path': '/daily-schedules'},
    ]

    return html.Div([
        # Logo Section - Improved
        html.Div([
            html.Div([
                # Animated train icon
                html.Div([
                    html.I(className="fas fa-train", style={
                        'fontSize': '42px',
                        'color': COLORS['accent'],
                        'marginBottom': '16px',
                        'filter': 'drop-shadow(0 4px 8px rgba(0,0,0,0.2))'
                    })
                ], style={'animation': 'float 3s ease-in-out infinite'}),
                html.H3("SL Railway", style={
                    'color': 'white',
                    'margin': '0',
                    'fontWeight': '800',
                    'fontSize': '24px',
                    'letterSpacing': '0.5px'
                }),
                html.P("TCDAFS v6.0", style={
                    'color': 'rgba(255,255,255,0.8)',
                    'fontSize': '12px',
                    'margin': '6px 0 0 0',
                    'padding': '4px 12px',
                    'background': 'rgba(255,255,255,0.1)',
                    'borderRadius': '12px',
                    'display': 'inline-block',
                    'fontWeight': '600'
                })
            ], style={'textAlign': 'center'})
        ], style={
            'padding': '36px 20px 32px 20px',
            'borderBottom': '2px solid rgba(255,255,255,0.15)',
            'background': 'linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0) 100%)'
        }),

        # FIXED: Navigation Links with active state based on current path
        html.Div([
            dcc.Link([
                html.I(className=item['icon'], style={
                    'marginRight': '16px',
                    'fontSize': '18px',
                    'width': '20px'
                }),
                html.Span(item['label'])
            ], href=item['path'], 
               id=f"nav-{item['path']}", 
               className="nav-link-item nav-link-active" if item['path'] == current_path else "nav-link-item",
               style=NAV_LINK_STYLE)
            for item in nav_items
        ], id="nav-container", style={'padding': '16px 0'}),

        # User Profile Section
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-user-circle", style={
                        'fontSize': '32px',
                        'color': 'white'
                    }),
                    html.Div([
                        html.P(email, id="sidebar-user-email", style={
                            'color': 'white',
                            'margin': '0',
                            'fontWeight': '600',
                            'fontSize': '14px',
                            'whiteSpace': 'nowrap',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': '180px'
                        }),
                        html.P(full_name, id="sidebar-user-name", style={
                            'color': 'rgba(255,255,255,0.7)',
                            'margin': '2px 0 0 0',
                            'fontSize': '13px'
                        })
                    ], style={'marginLeft': '12px'})
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'padding': '16px',
                    'background': 'rgba(255,255,255,0.1)',
                    'borderRadius': '8px',
                    'marginBottom': '12px'
                }, className="user-profile-box"),

                html.Button([
                    html.I(className="fas fa-sign-out-alt", style={'marginRight': '10px'}),
                    "Logout"
                ], id="sidebar-logout-btn", n_clicks=0, style={
                    'width': '100%',
                    'border': 'none',
                    'background': 'rgba(255,255,255,0.15)',
                    'color': 'white',
                    'padding': '12px',
                    'borderRadius': '8px',
                    'fontSize': '15px',
                    'fontWeight': '500',
                    'cursor': 'pointer',
                    'transition': 'all 0.3s ease'
                })
            ])
        ], style={
            'position': 'absolute',
            'bottom': '20px',
            'left': '16px',
            'right': '16px'
        })
    ], style=SIDEBAR_STYLE)
# ============= TOPBAR =============
def create_topbar():
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
# ============= STAT CARD =============
def create_stat_card(icon, value, label, color):
    return html.Div([
        html.Div([
            html.Div([
                html.I(className=icon, style={'fontSize': '32px', 'color': color}),
            ], style={
                'flex': '0 0 64px',
                'height': '64px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'background': f'{color}15',
                'borderRadius': '12px'
            }),
            html.Div([
                html.H3(value, style={
                    'margin': '0',
                    'fontSize': '28px',
                    'fontWeight': '700',
                    'color': COLORS['text_primary']
                }),
                html.P(label, style={
                    'margin': '0',
                    'color': COLORS['text_secondary'],
                    'fontSize': '14px',
                    'marginTop': '4px'
                })
            ], style={'marginLeft': '16px'})
        ], style={'display': 'flex', 'alignItems': 'center'})
    ], className="stat-card", style={
        'background': COLORS['surface'],
        'padding': '24px',
        'borderRadius': '12px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
        'border': f'1px solid {COLORS["border"]}'
    })
# ============= OVERVIEW LAYOUT =============
def overview_layout():
    return html.Div([
        create_topbar(),
        html.Div([
            # Header with gradient background
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-line", style={
                        'fontSize': '32px',
                        'color': COLORS['primary'],
                        'marginRight': '16px'
                    }),
                    html.Div([
                        html.H3("Dashboard Overview", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '28px'
                        }),
                        html.P("Real-time railway system analytics and performance metrics", style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '14px',
                            'margin': '4px 0 0 0'
                        })
                    ])
                ], style={
                    'display': 'flex',
                    'alignItems': 'center'
                })
            ], style={
                'background': f'linear-gradient(135deg, {COLORS["surface"]} 0%, #f8f9fa 100%)',
                'padding': '24px 30px',
                'marginBottom': '30px',
                'borderRadius': '16px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.06)',
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
                                    'fontSize': '20px'
                                }),
                                html.H5("Daily Ticket Sales Trend", style={
                                    'color': COLORS['text_primary'],
                                    'fontWeight': '600',
                                    'margin': '0',
                                    'display': 'inline'
                                }),
                            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'}),
                            html.P("Last 30 days ticket booking trends and revenue insights", style={
                                'color': COLORS['text_secondary'],
                                'fontSize': '13px',
                                'margin': '0'
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
                                    'fontSize': '18px'
                                }),
                                html.H5("Schedule Status Today", style={
                                    'color': COLORS['text_primary'],
                                    'fontWeight': '600',
                                    'margin': '0',
                                    'display': 'inline',
                                    'fontSize': '18px'
                                }),
                            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '6px'}),
                            html.P("Completed vs Pending Schedules", style={
                                'color': COLORS['text_secondary'],
                                'fontSize': '12px',
                                'margin': '0'
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
                                    'fontSize': '18px'
                                }),
                                html.H5("Class Distribution", style={
                                    'color': COLORS['text_primary'],
                                    'fontWeight': '600',
                                    'margin': '0',
                                    'display': 'inline',
                                    'fontSize': '18px'
                                }),
                            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '6px'}),
                            html.P("Today's bookings by class type", style={
                                'color': COLORS['text_secondary'],
                                'fontSize': '12px',
                                'margin': '0'
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
# ============= TICKET BOOKING LAYOUT =============
def ticket_layout():
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
                                            value=datetime.now().strftime("%Y-%m-%d")
                                        ),
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
                                    {"label": "Confirmed", "value": "Confirmed"}
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
# ============= TRAIN MODELS LAYOUT =============
def train_models_layout():
    return html.Div([
        create_topbar(),
        html.Div([
            # Enhanced Header with Gradient Background
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-train", style={
                            'fontSize': '36px',
                            'color': 'white'
                        })
                    ], style={
                        'width': '70px',
                        'height': '70px',
                        'borderRadius': '12px',
                        'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["primary_dark"]} 100%)',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'marginRight': '16px',
                        'boxShadow': '0 4px 12px rgba(196, 30, 58, 0.25)'
                    }),
                    html.Div([
                        html.H3("Train Models Management", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '26px'
                        }),
                        html.P([
                            html.I(className="fas fa-cogs", style={'marginRight': '6px'}),
                            "Manage railway train models, specifications, and route assignments"
                        ], style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '14px',
                            'margin': '6px 0 0 0'
                        })
                    ])
                ], style={'display': 'flex', 'alignItems': 'center'}),
                dbc.Button([
                    html.I(className="fas fa-plus-circle", style={'marginRight': '8px'}),
                    "Add New Model"
                ], id="add-train-model-btn", color="primary", size="lg")
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'background': f'linear-gradient(135deg, {COLORS["surface"]} 0%, #f8f9fa 100%)',
                'padding': '24px 28px',
                'marginBottom': '24px',
                'borderRadius': '16px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.06)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Alert for CRUD operations
            dbc.Alert(id="train-model-alert", is_open=False, duration=4000, dismissable=True, 
                     style={'marginBottom': '20px'}),

            # Enhanced Filter Section with Modern Design
            html.Div([
                # Filter Header
                html.Div([
                    html.Div([
                        html.I(className="fas fa-filter", style={
                            'marginRight': '12px',
                            'color': COLORS['primary'],
                            'fontSize': '18px'
                        }),
                        html.H5("Filter Models", style={
                            'margin': '0',
                            'fontWeight': '600',
                            'fontSize': '18px',
                            'color': COLORS['text_primary']
                        })
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    html.P("Refine your search using multiple criteria", style={
                        'margin': '6px 0 0 0',
                        'color': COLORS['text_secondary'],
                        'fontSize': '13px'
                    })
                ], style={
                    'padding': '20px 24px',
                    'borderBottom': f'1px solid {COLORS["border"]}',
                    'background': '#fafbfc'
                }),
                
                # Filter Controls
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-tag", style={'marginRight': '6px', 'fontSize': '12px'}),
                                "Model Name"
                            ], style={'fontWeight': '600', 'marginBottom': '8px', 'fontSize': '13px'}),
                            dcc.Dropdown(
                                id="filter-train-model-name",
                                placeholder="Select model...",
                                clearable=True,
                                searchable=True
                            ),
                        ], md=3),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-subway", style={'marginRight': '6px', 'fontSize': '12px'}),
                                "Model Type"
                            ], style={'fontWeight': '600', 'marginBottom': '8px', 'fontSize': '13px'}),
                            dcc.Dropdown(
                                id="filter-train-model-type",
                                placeholder="Select type...",
                                clearable=True,
                                searchable=True
                            ),
                        ], md=3),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-globe", style={'marginRight': '6px', 'fontSize': '12px'}),
                                "Country"
                            ], style={'fontWeight': '600', 'marginBottom': '8px', 'fontSize': '13px'}),
                            dcc.Dropdown(
                                id="filter-train-model-country",
                                placeholder="Select country...",
                                clearable=True,
                                searchable=True
                            ),
                        ], md=3),
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-industry", style={'marginRight': '6px', 'fontSize': '12px'}),
                                "Manufacturer"
                            ], style={'fontWeight': '600', 'marginBottom': '8px', 'fontSize': '13px'}),
                            dcc.Dropdown(
                                id="filter-train-model-manufacturer",
                                placeholder="Select manufacturer...",
                                clearable=True,
                                searchable=True
                            ),
                        ], md=3),
                    ], className="mb-3"),
                    
                    # Second Row: Routes and Action Buttons
                    dbc.Row([
                        dbc.Col([
                            dbc.Label([
                                html.I(className="fas fa-route", style={'marginRight': '6px', 'fontSize': '12px'}),
                                "Assigned Routes"
                            ], style={'fontWeight': '600', 'marginBottom': '8px', 'fontSize': '13px'}),
                            dcc.Dropdown(
                                id="filter-train-model-routes",
                                placeholder="Select route...",
                                clearable=True,
                                searchable=True
                            ),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("\u00A0", style={'marginBottom': '8px'}),
                            dbc.Button([
                                html.I(className="fas fa-search", style={'marginRight': '8px'}),
                                "Apply Filters"
                            ], id="apply-train-model-filter", color="primary", className="w-100"),
                        ], md=3),
                        dbc.Col([
                            dbc.Label("\u00A0", style={'marginBottom': '8px'}),
                            dbc.Button([
                                html.I(className="fas fa-times-circle", style={'marginRight': '8px'}),
                                "Clear All"
                            ], id="clear-train-model-filters", color="secondary", outline=True, className="w-100"),
                        ], md=3),
                    ])
                ], style={'padding': '24px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.06)',
                'border': f'1px solid {COLORS["border"]}',
                'marginBottom': '24px'
            }),

            # Enhanced Train Models Table with Modern Card Design
            html.Div([
                # Table Header
                html.Div([
                    html.Div([
                        html.I(className="fas fa-table", style={
                            'marginRight': '10px',
                            'color': COLORS['primary'],
                            'fontSize': '18px'
                        }),
                        html.H5("All Train Models", style={
                            'margin': '0',
                            'fontWeight': '600',
                            'fontSize': '18px',
                            'color': COLORS['text_primary']
                        })
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    html.Span([
                        html.I(className="fas fa-info-circle", style={
                            'marginRight': '6px',
                            'color': COLORS['info']
                        }),
                        "Click rows for details"
                    ], style={'fontSize': '13px', 'color': COLORS['text_secondary']})
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'padding': '20px 24px',
                    'borderBottom': f'1px solid {COLORS["border"]}',
                    'background': '#fafbfc'
                }),
                
                # Table Content
                html.Div(id="train-models-table", style={
                    'padding': '20px',
                    'minHeight': '400px',
                    'background': COLORS['surface']
                })
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.06)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Enhanced Add/Edit Modal with Modern Design
            dbc.Modal([
                dbc.ModalHeader([
                    html.I(className="fas fa-train", style={
                        'fontSize': '20px',
                        'color': COLORS['primary'],
                        'marginRight': '10px'
                    }),
                    dbc.ModalTitle(id="train-model-modal-title", style={
                        'fontSize': '20px',
                        'fontWeight': '600'
                    })
                ], style={
                    'borderBottom': f'1px solid {COLORS["border"]}',
                    'padding': '20px 24px',
                    'background': '#fafbfc'
                }),
                dbc.ModalBody([
                    # Basic Information Section
                    html.Div([
                        html.H6([
                            html.I(className="fas fa-info-circle", style={'marginRight': '8px'}),
                            "Basic Information"
                        ], style={'color': COLORS['primary'], 'fontWeight': '600', 'marginBottom': '16px', 'fontSize': '16px'}),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Model ID *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px'}),
                                dbc.Input(id="train-model-id", type="text", placeholder="e.g., S12EXP", maxLength=10),
                                html.Small("Uppercase letters & numbers, max 10 chars", className="text-muted")
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Model Name *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px'}),
                                dbc.Input(id="train-model-name", type="text", placeholder="e.g., S12 Express")
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Model Type *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px'}),
                                dbc.Input(id="train-model-type", type="text", placeholder="e.g., EMU")
                            ], md=4),
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Manufacturer *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px'}),
                                dbc.Input(id="train-model-manufacturer", type="text", placeholder="e.g., CRRC Corporation")
                            ], md=6),
                            dbc.Col([
                                dbc.Label("Country of Origin *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px'}),
                                dbc.Input(id="train-model-country", type="text", placeholder="e.g., China")
                            ], md=6),
                        ]),
                    ], style={
                        'padding': '20px',
                        'background': '#f8f9fa',
                        'borderRadius': '8px',
                        'marginBottom': '20px',
                        'border': f'1px solid {COLORS["border"]}'
                    }),
                    
                    # Capacity Information Section
                    html.Div([
                        html.H6([
                            html.I(className="fas fa-users", style={'marginRight': '8px'}),
                            "Capacity Details"
                        ], style={'color': COLORS['info'], 'fontWeight': '600', 'marginBottom': '16px', 'fontSize': '16px'}),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Operational Units *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px'}),
                                dbc.Input(id="train-model-operational-units", type="number", placeholder="e.g., 5", min=0)
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Compartments/Unit *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px'}),
                                dbc.Input(id="train-model-compartments-unit", type="number", placeholder="e.g., 4", min=1)
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Total Compartments *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px'}),
                                dbc.Input(id="train-model-total-compartments", type="number", placeholder="e.g., 20", min=0)
                            ], md=4),
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Seating/Compartment *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px'}),
                                dbc.Input(id="train-model-seating-capacity", type="number", placeholder="e.g., 60", min=0)
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Standing/Compartment *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px'}),
                                dbc.Input(id="train-model-standing-capacity", type="number", placeholder="e.g., 40", min=0)
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Total/Compartment *", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '6px'}),
                                dbc.Input(id="train-model-total-capacity", type="number", placeholder="e.g., 100", min=0)
                            ], md=4),
                        ]),
                    ], style={
                        'padding': '20px',
                        'background': '#f0f8ff',
                        'borderRadius': '8px',
                        'marginBottom': '20px',
                        'border': f'1px solid {COLORS["border"]}'
                    }),
                    
                    # Route Assignments Section
                    html.Div([
                        html.H6([
                            html.I(className="fas fa-route", style={'marginRight': '8px'}),
                            "Route Assignments"
                        ], style={'color': COLORS['success'], 'fontWeight': '600', 'marginBottom': '12px', 'fontSize': '16px'}),
                        html.P("Select all routes where this train model operates", 
                               style={'fontSize': '13px', 'color': COLORS['text_secondary'], 'marginBottom': '12px'}),
                        dbc.Checklist(
                            id="train-model-routes",
                            options=[
                                {"label": "R01", "value": "r01"},
                                {"label": "R02", "value": "r02"},
                                {"label": "R03", "value": "r03"},
                                {"label": "R04", "value": "r04"},
                                {"label": "R05", "value": "r05"},
                                {"label": "R06", "value": "r06"},
                                {"label": "R07", "value": "r07"},
                                {"label": "R08", "value": "r08"},
                                {"label": "R09", "value": "r09"},
                            ],
                            value=[],
                            inline=True,
                            style={'fontSize': '14px'}
                        ),
                    ], style={
                        'padding': '20px',
                        'background': '#f0fff4',
                        'borderRadius': '8px',
                        'border': f'1px solid {COLORS["border"]}'
                    }),
                ], style={'padding': '24px'}),
                
                dbc.ModalFooter([
                    dbc.Button([
                        html.I(className="fas fa-times", style={'marginRight': '8px'}),
                        "Cancel"
                    ], id="cancel-train-model-btn", color="secondary", outline=True),
                    dbc.Button([
                        html.I(className="fas fa-save", style={'marginRight': '8px'}),
                        "Save Model"
                    ], id="save-train-model-btn", color="primary"),
                ], style={
                    'borderTop': f'1px solid {COLORS["border"]}',
                    'padding': '16px 24px',
                    'background': '#fafbfc'
                })
            ], id="train-model-modal", size="xl", is_open=False),

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
                    html.P("Are you sure you want to delete this train model?", style={
                        'textAlign': 'center',
                        'fontSize': '16px',
                        'marginBottom': '8px'
                    }),
                    html.P(id="train-model-delete-name", style={
                        'textAlign': 'center',
                        'fontWeight': '600',
                        'color': COLORS['primary'],
                        'fontSize': '18px'
                    })
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-delete-train-model-btn", color="secondary", outline=True),
                    dbc.Button("Delete", id="confirm-delete-train-model-btn", color="danger"),
                ])
            ], id="train-model-delete-modal", is_open=False),

            # Hidden stores for state management
            dcc.Store(id="train-model-edit-id"),
            dcc.Store(id="train-model-delete-id"),
        ], style={'padding': '30px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
# ============= OPERATIONAL TRAINS LAYOUT =============
def trains_layout():
    return html.Div([
        create_topbar(),
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.I(className="fas fa-subway", style={
                        'fontSize': '32px',
                        'color': COLORS['primary'],
                        'marginRight': '16px'
                    }),
                    html.Div([
                        html.H3("Operational Trains Management", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '28px'
                        }),
                        html.P("Manage active trains in the railway system", style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '14px',
                            'margin': '4px 0 0 0'
                        })
                    ])
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '0'}),
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-plus", style={'marginRight': '8px'}),
                        "Add New Train"
                    ], id="add-operational-train-btn", style=BUTTON_PRIMARY)
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
            dbc.Alert(id="operational-train-alert", is_open=False, duration=4000, style={'marginBottom': '20px'}),

            # Filter Section
            html.Div([
                html.Div([
                    html.I(className="fas fa-filter", style={'marginRight': '10px', 'color': COLORS['primary']}),
                    html.H5("Filter Trains", style={'display': 'inline', 'margin': '0', 'fontWeight': '600'})
                ], style={'padding': '20px', 'borderBottom': f'1px solid {COLORS["border"]}'}),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Train Model", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="filter-operational-train-model",
                                placeholder="Select model...",
                                clearable=True
                            ),
                        ], width=4),
                        dbc.Col([
                            dbc.Label("Status", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="filter-operational-train-status",
                                options=[
                                    {"label": "Active", "value": "Active"},
                                    {"label": "Maintenance", "value": "Maintenance"},
                                    {"label": "Inactive", "value": "Inactive"}
                                ],
                                placeholder="Select status...",
                                clearable=True
                            ),
                        ], width=4),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-search", style={'marginRight': '8px'}),
                                "Apply Filter"
                            ], id="apply-operational-train-filter", style={**BUTTON_PRIMARY, 'marginTop': '28px', 'width': '100%'})
                        ], width=4),
                    ])
                ], style={'padding': '20px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}',
                'marginBottom': '24px'
            }),

            # Operational Trains Table
            html.Div([
                html.Div([
                    html.I(className="fas fa-list", style={'marginRight': '10px', 'color': COLORS['primary']}),
                    html.H5("All Operational Trains", style={'display': 'inline', 'margin': '0', 'fontWeight': '600'})
                ], style={'padding': '20px', 'borderBottom': f'1px solid {COLORS["border"]}'}),
                html.Div([
                    html.Div(id="trains-table", style={'minHeight': '300px'})
                ], style={'padding': '20px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Add/Edit Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="operational-train-modal-title")),
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Train Name *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(id="operational-train-name", type="text", placeholder="e.g., Udarata Menike"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Train Number *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(id="operational-train-number", type="text", placeholder="e.g., T001"),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Train Model *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(id="operational-train-model", placeholder="Select model..."),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Status *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="operational-train-status",
                                options=[
                                    {"label": "Active", "value": "Active"},
                                    {"label": "Maintenance", "value": "Maintenance"},
                                    {"label": "Inactive", "value": "Inactive"}
                                ],
                                value="Active"
                            ),
                        ], width=6),
                    ]),
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-operational-train-btn", color="secondary", outline=True),
                    dbc.Button("Save", id="save-operational-train-btn", style=BUTTON_PRIMARY),
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

            # Hidden stores for state management
            dcc.Store(id="operational-train-edit-id"),
            dcc.Store(id="operational-train-delete-id"),
        ], style={'padding': '30px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
# ============= ROUTES LAYOUT =============
def routes_layout():
    return html.Div([
        create_topbar(),
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.I(className="fas fa-route", style={
                        'fontSize': '32px',
                        'color': COLORS['primary'],
                        'marginRight': '16px'
                    }),
                    html.Div([
                        html.H3("Train Routes Management", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '28px'
                        }),
                        html.P("Manage railway routes and station connections", style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '14px',
                            'margin': '4px 0 0 0'
                        })
                    ])
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '0'}),
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-plus", style={'marginRight': '8px'}),
                        "Add New Route"
                    ], id="add-route-btn", style=BUTTON_PRIMARY)
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
            dbc.Alert(id="route-alert", is_open=False, duration=4000, style={'marginBottom': '20px'}),

            # Routes Table
            html.Div([
                html.Div([
                    html.I(className="fas fa-list", style={'marginRight': '10px', 'color': COLORS['primary']}),
                    html.H5("All Train Routes", style={'display': 'inline', 'margin': '0', 'fontWeight': '600'})
                ], style={'padding': '20px', 'borderBottom': f'1px solid {COLORS["border"]}'}),
                html.Div([
                    html.Div(id="routes-table", style={'minHeight': '300px'})
                ], style={'padding': '20px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Add/Edit Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="route-modal-title")),
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Route Name *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(id="route-name", type="text", placeholder="e.g., Colombo - Kandy Main Line"),
                        ], width=12),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Origin Station *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(id="route-origin", placeholder="Select origin station..."),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Destination Station *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(id="route-destination", placeholder="Select destination station..."),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Distance (km) *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(id="route-distance", type="number", placeholder="e.g., 120"),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Estimated Duration (minutes) *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(id="route-duration", type="number", placeholder="e.g., 180"),
                        ], width=6),
                    ]),
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-route-btn", color="secondary", outline=True),
                    dbc.Button("Save", id="save-route-btn", style=BUTTON_PRIMARY),
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
        ], style={'padding': '30px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
# ============= TRAIN SCHEDULES LAYOUT =============
def train_schedules_layout():
    return html.Div([
        create_topbar(),
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
                    html.I(className="fas fa-filter", style={'marginRight': '10px', 'color': COLORS['primary']}),
                    html.H5("Filter Schedules", style={'display': 'inline', 'margin': '0', 'fontWeight': '600'})
                ], style={'padding': '20px', 'borderBottom': f'1px solid {COLORS["border"]}'}),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Schedule Date", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(
                                id="filter-train-schedule-date",
                                type="date",
                                value=datetime.now().strftime("%Y-%m-%d")
                            ),
                        ], width=4),
                        dbc.Col([
                            dbc.Label("Origin Station", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="filter-train-schedule-origin",
                                placeholder="Select origin...",
                                clearable=True
                            ),
                        ], width=4),
                        dbc.Col([
                            dbc.Label("Destination Station", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="filter-train-schedule-destination",
                                placeholder="Select destination...",
                                clearable=True
                            ),
                        ], width=4),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-search", style={'marginRight': '8px'}),
                                "Apply Filter"
                            ], id="apply-train-schedule-filter", style={**BUTTON_PRIMARY, 'marginTop': '12px', 'width': '100%'})
                        ], width=4),
                    ])
                ], style={'padding': '20px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}',
                'marginBottom': '24px'
            }),

            # Train Schedules Table
            html.Div([
                html.Div([
                    html.I(className="fas fa-list-alt", style={'marginRight': '10px', 'color': COLORS['primary']}),
                    html.H5("All Train Schedules", style={'display': 'inline', 'margin': '0', 'fontWeight': '600'})
                ], style={'padding': '20px', 'borderBottom': f'1px solid {COLORS["border"]}'}),
                html.Div([
                    html.Div(id="train-schedules-table", style={'minHeight': '300px'})
                ], style={'padding': '20px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
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
# ============= TICKET PRICING LAYOUT =============
def ticket_pricing_layout():
    return html.Div([
        create_topbar(),
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.I(className="fas fa-dollar-sign", style={
                        'fontSize': '32px',
                        'color': COLORS['primary'],
                        'marginRight': '16px'
                    }),
                    html.Div([
                        html.H3("Ticket Pricing Management", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '700',
                            'margin': '0',
                            'fontSize': '28px'
                        }),
                        html.P("Manage station-to-station ticket prices", style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '14px',
                            'margin': '4px 0 0 0'
                        })
                    ])
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '0'}),
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-file-import", style={'marginRight': '8px'}),
                        "Bulk Import"
                    ], id="bulk-import-pricing-btn", color="secondary", outline=True, style={'marginRight': '12px'}),
                    dbc.Button([
                        html.I(className="fas fa-plus", style={'marginRight': '8px'}),
                        "Add New Price"
                    ], id="add-ticket-pricing-btn", style=BUTTON_PRIMARY)
                ], style={'marginLeft': 'auto', 'display': 'flex', 'alignItems': 'center'})
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
            dbc.Alert(id="ticket-pricing-alert", is_open=False, duration=4000, style={'marginBottom': '20px'}),

            # Search/Filter Section
            html.Div([
                html.Div([
                    html.I(className="fas fa-search", style={'marginRight': '10px', 'color': COLORS['primary']}),
                    html.H5("Search Ticket Prices", style={'display': 'inline', 'margin': '0', 'fontWeight': '600'})
                ], style={'padding': '20px', 'borderBottom': f'1px solid {COLORS["border"]}'}),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Origin Station", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="pricing-origin-station",
                                placeholder="Select origin station...",
                                searchable=True,
                                clearable=True
                            ),
                        ], width=5),
                        dbc.Col([
                            dbc.Label("Destination Station", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(
                                id="pricing-destination-station",
                                placeholder="Select destination station...",
                                searchable=True,
                                clearable=True
                            ),
                        ], width=5),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-search", style={'marginRight': '8px'}),
                                "Search"
                            ], id="search-pricing-btn", style={**BUTTON_PRIMARY, 'marginTop': '28px', 'width': '100%'})
                        ], width=2),
                    ])
                ], style={'padding': '20px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}',
                'marginBottom': '24px'
            }),

            # Pricing Table
            html.Div([
                html.Div([
                    html.I(className="fas fa-table", style={'marginRight': '10px', 'color': COLORS['primary']}),
                    html.H5("Ticket Prices", style={'display': 'inline', 'margin': '0', 'fontWeight': '600'})
                ], style={'padding': '20px', 'borderBottom': f'1px solid {COLORS["border"]}'}),
                html.Div([
                    html.Div(id="ticket-pricing-table", style={'minHeight': '300px'})
                ], style={'padding': '20px'})
            ], style={
                'background': COLORS['surface'],
                'borderRadius': '16px',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}'
            }),

            # Add/Edit Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="ticket-pricing-modal-title")),
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Origin Station *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(id="pricing-modal-origin", placeholder="Select origin..."),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Destination Station *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dcc.Dropdown(id="pricing-modal-destination", placeholder="Select destination..."),
                        ], width=6),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("First Class Price (LKR) *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(id="pricing-first-class", type="number", placeholder="e.g., 500"),
                        ], width=4),
                        dbc.Col([
                            dbc.Label("Second Class Price (LKR) *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(id="pricing-second-class", type="number", placeholder="e.g., 300"),
                        ], width=4),
                        dbc.Col([
                            dbc.Label("Third Class Price (LKR) *", style={'fontWeight': '500', 'marginBottom': '8px'}),
                            dbc.Input(id="pricing-third-class", type="number", placeholder="e.g., 150"),
                        ], width=4),
                    ]),
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-ticket-pricing-btn", color="secondary", outline=True),
                    dbc.Button("Save", id="save-ticket-pricing-btn", style=BUTTON_PRIMARY),
                ])
            ], id="ticket-pricing-modal", size="lg", is_open=False),

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
                    html.P("Are you sure you want to delete this pricing entry?", style={
                        'textAlign': 'center',
                        'fontSize': '16px',
                        'marginBottom': '8px'
                    }),
                    html.P(id="ticket-pricing-delete-name", style={
                        'textAlign': 'center',
                        'fontWeight': '600',
                        'color': COLORS['primary'],
                        'fontSize': '18px'
                    })
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-delete-pricing-btn", color="secondary", outline=True),
                    dbc.Button("Delete", id="confirm-delete-pricing-btn", color="danger"),
                ])
            ], id="ticket-pricing-delete-modal", is_open=False),

            # Bulk Import Modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Bulk Import Pricing")),
                dbc.ModalBody([
                    html.P("Upload a CSV file with columns: origin_station_id, destination_station_id, first_class_price, second_class_price, third_class_price",
                           style={'marginBottom': '16px', 'color': COLORS['text_secondary']}),
                    dcc.Upload(
                        id="upload-pricing-csv",
                        children=html.Div([
                            html.I(className="fas fa-cloud-upload-alt", style={'fontSize': '48px', 'color': COLORS['primary'], 'marginBottom': '12px'}),
                            html.P("Drag and Drop or Click to Select CSV File", style={'margin': '0'})
                        ]),
                        style={
                            'width': '100%',
                            'height': '150px',
                            'lineHeight': '150px',
                            'borderWidth': '2px',
                            'borderStyle': 'dashed',
                            'borderRadius': '12px',
                            'textAlign': 'center',
                            'borderColor': COLORS['border'],
                            'cursor': 'pointer',
                            'background': '#fafbfc'
                        },
                        multiple=False
                    ),
                    html.Div(id="upload-pricing-status", style={'marginTop': '16px'})
                ]),
                dbc.ModalFooter([
                    dbc.Button("Close", id="close-bulk-import-modal", color="secondary"),
                ])
            ], id="bulk-import-modal", size="lg", is_open=False),

            # Hidden stores for state management
            dcc.Store(id="ticket-pricing-edit-id"),
            dcc.Store(id="ticket-pricing-delete-id"),
        ], style={'padding': '30px', 'background': COLORS['background'], 'minHeight': '100vh'})
    ])
# ============= DAILY SCHEDULES LAYOUT =============
def daily_schedules_layout():
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
                        html.P("View and manage running schedules by date", style={
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
# ============= SCHEDULE BY STATION LAYOUT =============
def schedule_by_station_layout():
    return html.Div([
        create_topbar(),
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
# ============= MAIN LAYOUT =============
app.layout = html.Div([
    dcc.Store(id="token-store", storage_type="session"),
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])
# ============= CALLBACKS =============
@callback(
    Output("page-content", "children"),
    [Input("url", "pathname"),
     Input("token-store", "data")],
    prevent_initial_call=False
)
def display_page(pathname, token):
    if not token:
        return login_layout()

    # Default to "/" if pathname is None
    if not pathname:
        pathname = "/"

    username = token.get("username", "user@railway.lk")
    full_name = "Administrator"

    try:
        user_data = make_api_request("/users/me", token=token)
        if user_data and isinstance(user_data, dict):
            full_name = user_data.get("full_name", "Administrator")
            username = user_data.get("email", username)
    except Exception as e:
        logger.warning(f"Could not fetch user profile: {e}")

    if pathname == "/tickets":
        content = ticket_layout()
    elif pathname == "/train-models":
        content = train_models_layout()
    elif pathname == "/trains":
        content = trains_layout()
    elif pathname == "/routes":
        content = routes_layout()
    elif pathname == "/schedules":
        content = train_schedules_layout()
    elif pathname == "/schedule-stations":
        content = schedule_by_station_layout()
    elif pathname == "/pricing":
        content = ticket_pricing_layout()
    elif pathname == "/daily-schedules":
        content = daily_schedules_layout()
    else:
        content = overview_layout()

    # Pass current pathname to sidebar for active state
    return html.Div([
        create_sidebar(email=username, full_name=full_name, current_path=pathname),
        html.Div(content, style=CONTENT_STYLE)
    ])
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks && n_clicks > 0) {
            return null;
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("token-store", "data", allow_duplicate=True),
    Input("sidebar-logout-btn", "n_clicks"),
    prevent_initial_call=True
)
# Clientside callback to handle Adult/Child conditional fields
app.clientside_callback(
    """
    function(passengerType) {
        if (!passengerType) return window.dash_clientside.no_update;
        const isChild = passengerType === 'child';
        const parentDiv = document.querySelector('[id*="passenger-fields"]');
        if (parentDiv) {
            const nicInput = parentDiv.querySelector('[id*="passenger-nic"]');
            const contactInput = parentDiv.querySelector('[id*="passenger-contact"]');
            const nicLabel = parentDiv.querySelectorAll('label')[0];
            const contactLabel = parentDiv.querySelectorAll('label')[1];
            if (isChild) {
                if (nicInput) {
                    nicInput.disabled = true;
                    nicInput.value = '';
                    nicInput.placeholder = 'Not required for children';
                    nicInput.style.backgroundColor = '#f5f5f5';
                }
                if (contactInput) {
                    contactInput.disabled = true;
                    contactInput.value = '';
                    contactInput.placeholder = 'Not required for children';
                    contactInput.style.backgroundColor = '#f5f5f5';
                }
                if (nicLabel) nicLabel.textContent = 'NIC/Passport (Not Required)';
                if (contactLabel) contactLabel.textContent = 'Contact Number (Not Required)';
            } else {
                if (nicInput) {
                    nicInput.disabled = false;
                    nicInput.placeholder = '123456789V or AB1234567';
                    nicInput.style.backgroundColor = 'white';
                }
                if (contactInput) {
                    contactInput.disabled = false;
                    contactInput.placeholder = '0712345678';
                    contactInput.style.backgroundColor = 'white';
                }
                if (nicLabel) nicLabel.textContent = 'NIC/Passport *';
                if (contactLabel) contactLabel.textContent = 'Contact Number';
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("passenger-details-container", "children", allow_duplicate=True),
    Input({"type": "passenger-type", "index": dash.dependencies.ALL}, "value"),
    prevent_initial_call=True
)
@callback(
    [Output("token-store", "data"),
     Output("login-alert", "children"),
     Output("login-alert", "is_open"),
     Output("login-alert", "color"),
     Output("url", "pathname")],
    Input("login-button", "n_clicks"),
    [State("login-username", "value"),
     State("login-password", "value")],
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    if not n_clicks:
        return no_update, "", False, "danger", no_update

    if not username or not password:
        return no_update, "Please enter email and password", True, "warning", no_update

    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        if response.status_code == 200:
            token_data = response.json()
            return {
                "access_token": token_data["access_token"],
                "username": username
            }, "", False, "success", "/"
        else:
            return no_update, "Invalid email or password", True, "danger", no_update
    except Exception as e:
        return no_update, f"Login failed: {str(e)}", True, "danger", no_update

# ============= PROFILE DROPDOWN CALLBACKS =============
@callback(
    Output("profile-dropdown-menu", "style"),
    Input("profile-dropdown-btn", "n_clicks"),
    State("profile-dropdown-menu", "style"),
    prevent_initial_call=True
)
def toggle_profile_dropdown(n_clicks, current_style):
    """Toggle profile dropdown visibility"""
    if n_clicks:
        if current_style.get("display") == "none":
            current_style["display"] = "block"
        else:
            current_style["display"] = "none"
        return current_style
    return no_update

# ============= CHILD/ADULT TOGGLE BUTTONS CALLBACK =============
app.clientside_callback(
    """
    function(adult_clicks, child_clicks) {
        const triggered = dash_clientside.callback_context.triggered;
        if (!triggered || triggered.length === 0) return window.dash_clientside.no_update;

        const triggeredId = triggered[0].prop_id;

        // Determine which button was clicked and return appropriate value
        if (triggeredId.includes('adult')) {
            return 'adult';
        } else if (triggeredId.includes('child')) {
            return 'child';
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output({"type": "passenger-type", "index": dash.dependencies.MATCH}, "value"),
    Input({"type": "passenger-type-btn-adult", "index": dash.dependencies.MATCH}, "n_clicks"),
    Input({"type": "passenger-type-btn-child", "index": dash.dependencies.MATCH}, "n_clicks"),
    prevent_initial_call=True
)

@callback(
    [Output("stat-card-1", "children"),
     Output("stat-card-2", "children"),
     Output("stat-card-3", "children"),
     Output("stat-card-4", "children")],
    [Input("overview-interval", "n_intervals"),
     Input("url", "pathname")],
    State("token-store", "data")
)
def update_stats(n, pathname, token):
    default = [
        create_stat_card("fas fa-train", "0", "Trains Active Today", COLORS['primary']),
        create_stat_card("fas fa-calendar-check", "0", "Trains Scheduled Today", COLORS['info']),
        create_stat_card("fas fa-ticket-alt", "0", "Tickets Booked Today", COLORS['success']),
        create_stat_card("fas fa-dollar-sign", "LKR 0", "Revenue Today", COLORS['warning'])
    ]
    if not token or pathname != "/":
        return default
    data = make_api_request("/analytics/summary", token=token)
    if data:
        return [
            create_stat_card("fas fa-train", str(data.get("trains_active_today", 0)),
                           "Trains Active Today", COLORS['primary']),
            create_stat_card("fas fa-calendar-check", str(data.get("trains_scheduled_today", 0)),
                           "Trains Scheduled Today", COLORS['info']),
            create_stat_card("fas fa-ticket-alt", str(data.get("total_tickets_today", 0)),
                           "Tickets Booked Today", COLORS['success']),
            create_stat_card("fas fa-dollar-sign", f"LKR {float(data.get('revenue_today', 0)):,.2f}",
                           "Revenue Today", COLORS['warning'])
        ]
    return default
@callback(
    Output("daily-ticket-sales-chart", "figure"),
    [Input("overview-interval", "n_intervals"),
     Input("url", "pathname")],
    State("token-store", "data")
)
def update_daily_ticket_sales_chart(n, pathname, token):
    fig = go.Figure()
    if not token or pathname != "/":
        return fig
    data = make_api_request("/analytics/daily-ticket-sales", token=token)
    if data:
        fig.add_trace(go.Scatter(
            x=data.get("dates", []),
            y=data.get("tickets", []),
            mode='lines+markers',
            line=dict(color=COLORS['primary'], width=3),
            marker=dict(size=8, color=COLORS['primary']),
            fill='tozeroy',
            fillcolor=f'rgba(196, 30, 58, 0.1)',
            name='Tickets Sold'
        ))
        fig.update_layout(
            template="plotly_white",
            height=280,
            margin=dict(l=40, r=20, t=10, b=40),
            xaxis=dict(
                title="Date",
                showgrid=False
            ),
            yaxis=dict(
                title="Number of Tickets",
                showgrid=True,
                gridcolor='#f1f5f9'
            ),
            hovermode='x unified',
            showlegend=False
        )
    return fig
@callback(
    Output("schedule-status-pie", "figure"),
    [Input("overview-interval", "n_intervals"),
     Input("url", "pathname")],
    State("token-store", "data")
)
def update_schedule_status_pie(n, pathname, token):
    fig = go.Figure()
    if not token or pathname != "/":
        return fig
    data = make_api_request("/analytics/schedule-status-today", token=token)
    if data:
        labels = ['Completed', 'Pending']
        values = [data.get('completed', 0), data.get('pending', 0)]
        colors_pie = [COLORS['success'], COLORS['warning']]
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors_pie),
            hole=0.4,
            textinfo='label+percent+value',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Schedules: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        fig.update_layout(
            template="plotly_white",
            height=280,
            margin=dict(l=20, r=20, t=10, b=20),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
    return fig
@callback(
    Output("class-distribution-pie", "figure"),
    [Input("overview-interval", "n_intervals"),
     Input("url", "pathname")],
    State("token-store", "data")
)
def update_class_distribution_pie(n, pathname, token):
    fig = go.Figure()
    if not token or pathname != "/":
        return fig
    data = make_api_request("/analytics/class-distribution-today", token=token)
    if data:
        labels = ['1st Class', '2nd Class', '3rd Class']
        values = [
            data.get('first_class', 0),
            data.get('second_class', 0),
            data.get('third_class', 0)
        ]
        colors_pie = [COLORS['primary'], COLORS['info'], COLORS['success']]
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors_pie),
            hole=0.4,
            textinfo='label+percent+value',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Tickets: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        fig.update_layout(
            template="plotly_white",
            height=280,
            margin=dict(l=20, r=20, t=10, b=20),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
    return fig
@callback(
    Output("ticket-origin", "options"),
    Input("url", "pathname"),
    State("token-store", "data"),
    prevent_initial_call=False
)
def load_origin_stations(pathname, token):
    if pathname != "/tickets":
        return []
    # Stations endpoint doesn't require authentication
    stations = make_api_request("/stations", token=None)
    if stations and isinstance(stations, list):
        try:
            opts = [{"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")} for s in stations]
            logger.info(f"Loaded {len(opts)} stations for ticket booking")
            return opts
        except Exception as e:
            logger.error(f"Error processing stations: {e}")
            return []
    else:
        logger.warning("No stations data received from API or invalid format")
        return []

@callback(
    Output("ticket-destination", "options"),
    [Input("url", "pathname"),
     Input("ticket-origin", "value")],
    State("token-store", "data"),
    prevent_initial_call=False
)
def load_destination_stations(pathname, origin_value, token):
    """Load destination stations, excluding the selected origin"""
    if pathname != "/tickets":
        return []

    stations = make_api_request("/stations", token=None)
    if stations and isinstance(stations, list):
        try:
            # Exclude the origin station from destination options
            opts = [
                {"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")}
                for s in stations
                if s.get("station_id") != origin_value
            ]
            return opts
        except Exception as e:
            logger.error(f"Error processing stations: {e}")
            return []
    else:
        return []
@callback(
    Output("available-schedules", "children"),
    [Input("ticket-origin", "value"),
     Input("ticket-destination", "value"),
     Input("ticket-date", "value")],
    State("token-store", "data")
)
def load_schedules_display(origin, dest, date, token):
    if not all([origin, dest, date, token]):
        return html.Div()

    # Use the correct API endpoint - /schedules/available with travel_date parameter
    endpoint = f"/schedules/available?origin_station_id={origin}&destination_station_id={dest}&travel_date={date}"
    schedules = make_api_request(endpoint, token=token)

    if not schedules or not isinstance(schedules, list) or len(schedules) == 0:
        logger.warning(f"No schedules found for origin={origin}, dest={dest}, date={date}")

        # Get day of week for better error message
        from datetime import datetime as dt
        try:
            date_obj = dt.strptime(date, "%Y-%m-%d")
            day_name = date_obj.strftime("%A")
        except:
            day_name = "selected day"

        return dbc.Alert([
            html.I(className="fas fa-info-circle", style={'marginRight': '8px', 'fontSize': '20px'}),
            html.Div([
                html.Strong("No trains found for this route", style={'display': 'block', 'marginBottom': '8px'}),
                html.P(f"Travel date: {date} ({day_name})", style={'margin': '4px 0', 'fontSize': '13px'}),
                html.P("Possible reasons:", style={'fontWeight': '600', 'marginTop': '12px', 'marginBottom': '6px'}),
                html.Ul([
                    html.Li(f"No trains operate on this route on {day_name}s"),
                    html.Li("The stations are not on the same train route"),
                    html.Li("Schedules for this route are inactive"),
                    html.Li("Try selecting a different date or route")
                ], style={'marginTop': '8px', 'marginBottom': '8px', 'fontSize': '13px'}),
                html.Hr(style={'margin': '12px 0'}),
                html.P([
                    html.I(className="fas fa-lightbulb", style={'marginRight': '6px', 'color': COLORS['warning']}),
                    html.Strong("Tip: "),
                    "Check the 'Schedule by Station' tab to see all trains operating from your origin station."
                ], style={'fontSize': '12px', 'color': COLORS['text_secondary']})
            ])
        ], color="warning", style={'padding': '20px'})
    schedule_cards = []
    for s in schedules:
        # Extract schedule information - backend returns these fields:
        # train_schedule_id, train_schedule, route_id, origin_station, origin_departure,
        # destination_station, destination_departure, duration
        train_name = s.get('train_schedule', 'N/A')
        origin_departure = s.get('origin_departure', 'N/A')
        destination_arrival = s.get('destination_departure', 'N/A')  # Backend calls it destination_departure

        # Parse duration string (format: "HH:MM:SS" or similar)
        duration_str = s.get('duration', '')
        if duration_str and isinstance(duration_str, str):
            try:
                # Parse duration like "2:30:00" or "2:30"
                parts = duration_str.split(':')
                hours = int(parts[0]) if len(parts) > 0 else 0
                mins = int(parts[1]) if len(parts) > 1 else 0
                if hours > 0:
                    duration_text = f"{hours}h {mins}m"
                else:
                    duration_text = f"{mins} minutes"
            except (ValueError, IndexError):
                duration_text = duration_str
        else:
            duration_text = "Duration not available"

        # Get available classes - backend doesn't return this yet, so default to all classes
        available_classes = s.get('available_classes', ['First', 'Second', 'Third'])
        if isinstance(available_classes, str):
            available_classes = [c.strip() for c in available_classes.split(',') if c.strip()]
        elif not isinstance(available_classes, list):
            available_classes = ['First', 'Second', 'Third']  # Default to all classes

        # Create class badges
        class_badges = []
        class_colors_map = {'First': COLORS['primary'], 'Second': COLORS['info'], 'Third': COLORS['success']}
        for cls in available_classes:
            class_badges.append(
                html.Span(cls, style={
                    'padding': '2px 8px',
                    'background': class_colors_map.get(cls, COLORS['text_secondary']),
                    'color': 'white',
                    'borderRadius': '4px',
                    'fontSize': '10px',
                    'fontWeight': '600',
                    'marginLeft': '4px'
                })
            )

        schedule_cards.append(
            html.Div([
                dbc.RadioItems(
                    id={"type": "schedule-radio", "index": s["train_schedule_id"]},
                    options=[{
                        "label": html.Div([
                            html.Div([
                                html.I(className="fas fa-train", style={'marginRight': '12px', 'color': COLORS['primary'], 'fontSize': '24px'}),
                                html.Div([
                                    html.Div([
                                        html.Strong(train_name, style={'fontSize': '16px', 'marginRight': '8px'}),
                                        *class_badges
                                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '4px'}),
                                    html.Div([
                                        html.I(className="fas fa-clock", style={'marginRight': '6px', 'fontSize': '11px'}),
                                        html.Span(f"Departs: {origin_departure}", style={'marginRight': '12px', 'fontSize': '13px'}),
                                        html.I(className="fas fa-flag-checkered", style={'marginRight': '6px', 'fontSize': '11px'}),
                                        html.Span(f"Arrives: {destination_arrival}", style={'fontSize': '13px'})
                                    ], style={'color': COLORS['text_secondary'], 'marginBottom': '2px'}),
                                    html.Div([
                                        html.I(className="fas fa-hourglass-half", style={'marginRight': '6px', 'fontSize': '11px'}),
                                        html.Span(f"Duration: {duration_text}", style={'fontSize': '12px', 'color': COLORS['info'], 'fontWeight': '500'})
                                    ])
                                ], style={'flex': '1'})
                            ], style={'display': 'flex', 'alignItems': 'center', 'width': '100%'})
                        ]),
                        "value": s["train_schedule_id"]
                    }],
                    value=None
                ),
                # Hidden div to store available classes for this schedule
                html.Div(
                    ','.join(available_classes) if available_classes else '',
                    id={"type": "schedule-classes", "index": s["train_schedule_id"]},
                    style={'display': 'none'}
                )
            ], style={
                'padding': '16px',
                'background': '#f8fafc',
                'borderRadius': '8px',
                'marginBottom': '12px',
                'border': f'2px solid {COLORS["border"]}',
                'cursor': 'pointer',
                'transition': 'all 0.3s ease'
            }, className="schedule-option")
        )
    return html.Div([
        html.Label("Available Train Schedules *", style={'fontWeight': '600', 'marginBottom': '12px'}),
        html.P("Click on a schedule to select it for booking", style={
            'fontSize': '12px',
            'color': COLORS['text_secondary'],
            'marginBottom': '8px'
        }),
        html.Div(schedule_cards)
    ])
# Callback to store selected schedule and update class options
@callback(
    [Output("selected-schedule-store", "data"),
     Output("ticket-class", "options"),
     Output("ticket-class", "value")],
    [Input({"type": "schedule-radio", "index": dash.dependencies.ALL}, "value")],
    [State({"type": "schedule-classes", "index": dash.dependencies.ALL}, "children")],
    prevent_initial_call=True
)
def store_selected_schedule_and_update_classes(selected_values, available_classes_list):
    """Store the selected train schedule and update available class options"""
    if not selected_values:
        return None, [], None

    # Find the first non-None value (selected schedule) and its index
    selected_schedule_id = None
    selected_index = None
    for idx, val in enumerate(selected_values):
        if val is not None:
            selected_schedule_id = val
            selected_index = idx
            break

    if selected_schedule_id is None:
        return None, [], None

    # Get the available classes for the selected schedule
    available_classes_str = available_classes_list[selected_index] if selected_index < len(available_classes_list) else ""
    available_classes = [c.strip() for c in available_classes_str.split(',') if c.strip()] if available_classes_str else []

    # Create class options based on what's available
    class_options = []
    class_labels = {"First": "1st Class", "Second": "2nd Class", "Third": "3rd Class"}

    if available_classes:
        for cls in available_classes:
            class_options.append({"label": class_labels.get(cls, cls), "value": cls})
    else:
        # Fallback to all classes if none specified
        class_options = [
            {"label": "1st Class", "value": "First"},
            {"label": "2nd Class", "value": "Second"},
            {"label": "3rd Class", "value": "Third"}
        ]

    # Set default value to the first available class
    default_value = class_options[0]["value"] if class_options else None

    return selected_schedule_id, class_options, default_value
@callback(
    [Output("ticket-alert", "children"),
     Output("ticket-alert", "is_open"),
     Output("ticket-alert", "color")],
    Input("book-ticket-btn", "n_clicks"),
    [State("ticket-origin", "value"),
     State("ticket-destination", "value"),
     State("selected-schedule-store", "data"),
     State("ticket-class", "value"),
     State("ticket-date", "value"),
     State("ticket-count-store", "data"),
     State({"type": "passenger-nic", "index": dash.dependencies.ALL}, "value"),
     State({"type": "passenger-contact", "index": dash.dependencies.ALL}, "value"),
     State({"type": "passenger-type", "index": dash.dependencies.ALL}, "value"),
     State("token-store", "data")],
    prevent_initial_call=True
)
def book_ticket(n, origin, dest, sched, cls, date, ticket_count, nic_list, contact_list, type_list, token):
    if not n or not token:
        return "", False, "danger"
    # Validate required fields
    if not all([origin, dest, sched, cls, date]):
        return "Please fill all required fields (origin, destination, schedule, class, date)", True, "warning"
    if not ticket_count or ticket_count < 1:
        return "Please select at least one ticket", True, "warning"
    # Book tickets for each passenger
    booked_tickets = []
    failed_bookings = 0
    for i in range(ticket_count):
        passenger_nic = nic_list[i] if i < len(nic_list) else None
        passenger_contact = contact_list[i] if i < len(contact_list) else None
        passenger_type = type_list[i] if i < len(type_list) else "adult"
        is_child = (passenger_type == "child")
        # Validate adult passengers have NIC
        if not is_child and not passenger_nic:
            return f"Please enter NIC/Passport for Passenger {i+1} (Adult)", True, "warning"
        # For children, NIC and contact are optional
        if is_child:
            passenger_nic = passenger_nic or "CHILD"
            passenger_contact = passenger_contact or None
        # Schema v2.0: Split NIC/Passport into separate fields
        ticket_data = {
            "schedule_date": date,
            "schedule_id": sched,
            "origin_station_id": origin,
            "destination_station_id": dest,
            "class": cls,
            "contact_number": passenger_contact,
            "payment_method": "Cash",
            "booking_platform": "Web",
            "is_child": is_child
        }
        # Add either NIC or Passport (v2.0 schema has separate fields)
        if passenger_nic and passenger_nic != "CHILD":
            # Simple heuristic: if contains letters, likely passport
            if any(c.isalpha() for c in passenger_nic.replace('V', '').replace('X', '')):
                ticket_data["passport"] = passenger_nic
            else:
                ticket_data["nic"] = passenger_nic
        # For children, NIC not required in v2.0
        result = make_api_request("/tickets", method="POST", token=token, data=ticket_data)
        if result:
            booked_tickets.append(result['ticket_id'])
        else:
            failed_bookings += 1
    # Return summary
    if len(booked_tickets) == ticket_count:
        ticket_ids = ", ".join(booked_tickets)
        return f"✅ All {ticket_count} ticket(s) booked successfully! IDs: {ticket_ids}", True, "success"
    elif len(booked_tickets) > 0:
        ticket_ids = ", ".join(booked_tickets)
        return f"⚠️ Partially successful: {len(booked_tickets)} booked ({ticket_ids}), {failed_bookings} failed", True, "warning"
    else:
        return f"❌ All bookings failed. Please check your details and try again.", True, "danger"
@callback(
    Output("trains-table", "children"),
    Input("url", "pathname"),
    State("token-store", "data")
)
def load_trains(pathname, token):
    if pathname != "/trains" or not token:
        return html.P("Loading...")

    trains = make_api_request("/trains", token=token)
    if not trains:
        return html.P("No trains found")

    df = pd.DataFrame(trains)
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={
            'backgroundColor': COLORS['primary'],
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8fafc'}
        ]
    )
@callback(
    Output("routes-table", "children"),
    Input("url", "pathname"),
    State("token-store", "data")
)
def load_routes(pathname, token):
    if pathname != "/routes" or not token:
        return html.P("Loading...")

    routes = make_api_request("/routes", token=token)
    if not routes:
        return html.P("No routes found")

    df = pd.DataFrame(routes)
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={
            'backgroundColor': COLORS['primary'],
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8fafc'}
        ]
    )

# ============= TRAIN MODELS CALLBACKS =============
@callback(
    Output("train-models-table", "children"),
    [Input("url", "pathname"),
     Input("apply-train-model-filter", "n_clicks")],
    [State("token-store", "data"),
     State("filter-train-model-name", "value"),
     State("filter-train-model-type", "value"),
     State("filter-train-model-country", "value"),
     State("filter-train-model-manufacturer", "value"),
     State("filter-train-model-routes", "value")]
)
def load_train_models(pathname, n_clicks, token, model_name_filter, model_type_filter, 
                      country_filter, manufacturer_filter, routes_filter):
    if pathname != "/train-models" or not token:
        return html.P("Loading...")

    train_models = make_api_request("/train-models", token=token)
    if not train_models:
        return html.Div([
            html.I(className="fas fa-info-circle", style={
                'fontSize': '48px',
                'color': COLORS['text_secondary'],
                'display': 'block',
                'textAlign': 'center',
                'marginBottom': '16px'
            }),
            html.P("No train models found", style={
                'textAlign': 'center',
                'color': COLORS['text_secondary'],
                'fontSize': '16px'
            })
        ], style={'padding': '40px'})

    df = pd.DataFrame(train_models)
    
    # Apply filters
    if model_name_filter:
        df = df[df['model_name'] == model_name_filter]
    
    if model_type_filter:
        df = df[df['model_type'] == model_type_filter]
    
    if country_filter:
        df = df[df['country_of_origin'] == country_filter]
    
    if manufacturer_filter:
        df = df[df['manufacturer'] == manufacturer_filter]
    
    if routes_filter:
        # Filter by route boolean column (r01-r09)
        route_col = routes_filter.lower()  # e.g., 'R01' -> 'r01'
        if route_col in df.columns:
            df = df[df[route_col] == True]
    
    if df.empty:
        return html.Div([
            html.I(className="fas fa-search", style={
                'fontSize': '48px',
                'color': COLORS['text_secondary'],
                'display': 'block',
                'textAlign': 'center',
                'marginBottom': '16px'
            }),
            html.P("No train models match your filters", style={
                'textAlign': 'center',
                'color': COLORS['text_secondary'],
                'fontSize': '16px'
            })
        ], style={'padding': '40px'})
    
    # Create assigned routes column by combining r01-r09 boolean values
    route_cols = ['r01', 'r02', 'r03', 'r04', 'r05', 'r06', 'r07', 'r08', 'r09']
    df['assigned_routes_display'] = df.apply(
        lambda row: ', '.join([col.upper() for col in route_cols if col in df.columns and row.get(col, False)]),
        axis=1
    )
    
    # Select and rename columns for display
    display_columns = [
        'model_id', 'model_name', 'model_type', 'manufacturer', 
        'country_of_origin', 'assigned_routes_display', 'operational_units', 
        'compartments_per_unit', 'total_compartments_assigned_per_model', 
        'seating_passengers_per_compartment', 'standing_passengers_per_compartment', 
        'total_passengers_per_compartment'
    ]
    
    # Filter to only show existing columns
    display_columns = [col for col in display_columns if col in df.columns]
    df_display = df[display_columns]
    
    # Create column mapping for better display names
    column_names = {
        'model_id': 'Model ID',
        'model_name': 'Model Name',
        'model_type': 'Model Type',
        'manufacturer': 'Manufacturer',
        'country_of_origin': 'Country of Origin',
        'assigned_routes_display': 'Assigned Routes',
        'operational_units': 'Operational Units',
        'compartments_per_unit': 'Compartments/Unit',
        'total_compartments_assigned_per_model': 'Total Compartments',
        'seating_passengers_per_compartment': 'Seats/Compartment',
        'standing_passengers_per_compartment': 'Standing/Compartment',
        'total_passengers_per_compartment': 'Total/Compartment'
    }
    
    return dash_table.DataTable(
        data=df_display.to_dict('records'),
        columns=[{"name": column_names.get(i, i), "id": i} for i in df_display.columns],
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontSize': '14px',
            'fontFamily': 'Roboto, sans-serif'
        },
        style_header={
            'backgroundColor': COLORS['primary'],
            'color': 'white',
            'fontWeight': '600',
            'fontSize': '14px',
            'padding': '14px',
            'border': 'none'
        },
        style_data={
            'border': 'none',
            'borderBottom': f'1px solid {COLORS["border"]}'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8fafc'
            },
            {
                'if': {'row_index': 'even'},
                'backgroundColor': 'white'
            }
        ],
        style_table={
            'overflowX': 'auto'
        },
        page_size=10,
        sort_action='native',
        filter_action='native'
    )

@callback(
    Output("filter-train-model-name", "options"),
    Input("url", "pathname"),
    State("token-store", "data")
)
def populate_model_name_filter(pathname, token):
    if pathname != "/train-models" or not token:
        return []

    train_models = make_api_request("/train-models", token=token)
    if not train_models:
        return []
    
    # Get unique model names
    model_names = sorted(list(set([model['model_name'] for model in train_models if model.get('model_name')])))
    return [{"label": name, "value": name} for name in model_names]

@callback(
    Output("filter-train-model-type", "options"),
    Input("url", "pathname"),
    State("token-store", "data")
)
def populate_model_type_filter(pathname, token):
    if pathname != "/train-models" or not token:
        return []

    train_models = make_api_request("/train-models", token=token)
    if not train_models:
        return []
    
    # Get unique model types
    model_types = sorted(list(set([model['model_type'] for model in train_models if model.get('model_type')])))
    return [{"label": mtype, "value": mtype} for mtype in model_types]

@callback(
    Output("filter-train-model-country", "options"),
    Input("url", "pathname"),
    State("token-store", "data")
)
def populate_country_filter(pathname, token):
    if pathname != "/train-models" or not token:
        return []

    train_models = make_api_request("/train-models", token=token)
    if not train_models:
        return []
    
    # Get unique countries
    countries = sorted(list(set([model['country_of_origin'] for model in train_models if model.get('country_of_origin')])))
    return [{"label": country, "value": country} for country in countries]

@callback(
    Output("filter-train-model-manufacturer", "options"),
    Input("url", "pathname"),
    State("token-store", "data")
)
def populate_manufacturer_filter(pathname, token):
    if pathname != "/train-models" or not token:
        return []

    train_models = make_api_request("/train-models", token=token)
    if not train_models:
        return []
    
    # Get unique manufacturers
    manufacturers = sorted(list(set([model['manufacturer'] for model in train_models if model.get('manufacturer')])))
    return [{"label": mfr, "value": mfr} for mfr in manufacturers]

@callback(
    Output("filter-train-model-routes", "options"),
    Input("url", "pathname"),
    State("token-store", "data")
)
def populate_routes_filter(pathname, token):
    if pathname != "/train-models" or not token:
        return []

    train_models = make_api_request("/train-models", token=token)
    if not train_models:
        return []
    
    # Get available routes from the boolean columns (r01-r09)
    df = pd.DataFrame(train_models)
    route_cols = ['r01', 'r02', 'r03', 'r04', 'r05', 'r06', 'r07', 'r08', 'r09']
    
    # Find which route columns exist and have at least one True value
    available_routes = []
    for col in route_cols:
        if col in df.columns and df[col].any():
            available_routes.append(col.upper())
    
    # Return all routes R01-R09 as options (even if not yet assigned)
    all_routes = ['R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08', 'R09']
    return [{"label": route, "value": route} for route in all_routes]

# ============= CLEAR FILTERS CALLBACK =============
@callback(
    [Output("filter-train-model-name", "value"),
     Output("filter-train-model-type", "value"),
     Output("filter-train-model-country", "value"),
     Output("filter-train-model-manufacturer", "value"),
     Output("filter-train-model-routes", "value")],
    Input("clear-train-model-filters", "n_clicks"),
    prevent_initial_call=True
)
def clear_train_model_filters(n_clicks):
    """Clear all train model filters"""
    return None, None, None, None, None

# ============= OPEN ADD MODEL MODAL CALLBACK =============
@callback(
    [Output("train-model-modal", "is_open"),
     Output("train-model-modal-title", "children")],
    [Input("add-train-model-btn", "n_clicks"),
     Input("cancel-train-model-btn", "n_clicks"),
     Input("save-train-model-btn", "n_clicks")],
    State("train-model-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_train_model_modal(add_clicks, cancel_clicks, save_clicks, is_open):
    """Toggle train model add/edit modal"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, "Add New Train Model"
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "add-train-model-btn":
        return True, "Add New Train Model"
    elif button_id in ["cancel-train-model-btn", "save-train-model-btn"]:
        return False, "Add New Train Model"
    
    return is_open, "Add New Train Model"

# ============= SAVE NEW TRAIN MODEL CALLBACK =============
@callback(
    [Output("train-model-alert", "children"),
     Output("train-model-alert", "is_open"),
     Output("train-model-alert", "color"),
     Output("train-model-id", "value"),
     Output("train-model-name", "value"),
     Output("train-model-type", "value"),
     Output("train-model-manufacturer", "value"),
     Output("train-model-country", "value"),
     Output("train-model-operational-units", "value"),
     Output("train-model-compartments-unit", "value"),
     Output("train-model-total-compartments", "value"),
     Output("train-model-seating-capacity", "value"),
     Output("train-model-standing-capacity", "value"),
     Output("train-model-total-capacity", "value"),
     Output("train-model-routes", "value"),
     Output("train-models-table", "children", allow_duplicate=True)],
    Input("save-train-model-btn", "n_clicks"),
    [State("train-model-id", "value"),
     State("train-model-name", "value"),
     State("train-model-type", "value"),
     State("train-model-manufacturer", "value"),
     State("train-model-country", "value"),
     State("train-model-operational-units", "value"),
     State("train-model-compartments-unit", "value"),
     State("train-model-total-compartments", "value"),
     State("train-model-seating-capacity", "value"),
     State("train-model-standing-capacity", "value"),
     State("train-model-total-capacity", "value"),
     State("train-model-routes", "value"),
     State("token-store", "data")],
    prevent_initial_call=True
)
def save_train_model(n_clicks, model_id, model_name, model_type, manufacturer, country,
                     operational_units, compartments_unit, total_compartments,
                     seating_capacity, standing_capacity, total_capacity, routes, token):
    """Save new train model to database"""
    if not n_clicks or not token:
        return no_update, False, "info", *([no_update] * 13)
    
    # Validation
    if not all([model_id, model_name, model_type, manufacturer, country]):
        return "Please fill in all required fields marked with *", True, "danger", *([no_update] * 13)
    
    if not all([operational_units is not None, compartments_unit, total_compartments,
                seating_capacity is not None, standing_capacity is not None, total_capacity is not None]):
        return "Please fill in all capacity fields", True, "danger", *([no_update] * 13)
    
    # Validate model_id format (uppercase letters and numbers only, max 10 chars)
    import re
    if not re.match(r'^[A-Z0-9]{1,10}$', model_id):
        return "Model ID must be 1-10 uppercase letters/numbers only", True, "danger", *([no_update] * 13)
    
    # Build route assignment dictionary
    route_data = {
        'r01': 'r01' in (routes or []),
        'r02': 'r02' in (routes or []),
        'r03': 'r03' in (routes or []),
        'r04': 'r04' in (routes or []),
        'r05': 'r05' in (routes or []),
        'r06': 'r06' in (routes or []),
        'r07': 'r07' in (routes or []),
        'r08': 'r08' in (routes or []),
        'r09': 'r09' in (routes or []),
    }
    
    # Prepare data payload
    data = {
        "model_id": model_id,
        "model_name": model_name,
        "model_type": model_type,
        "manufacturer": manufacturer,
        "country_of_origin": country,
        "operational_units": int(operational_units),
        "compartments_per_unit": int(compartments_unit),
        "total_compartments_assigned_per_model": int(total_compartments),
        "seating_passengers_per_compartment": int(seating_capacity),
        "standing_passengers_per_compartment": int(standing_capacity),
        "total_passengers_per_compartment": int(total_capacity),
        **route_data
    }
    
    # Make API request
    result = make_api_request("/train-models", method="POST", token=token, data=data)
    
    if result and not isinstance(result, dict) or (isinstance(result, dict) and 'error' not in result):
        # Success - clear form and reload table
        train_models = make_api_request("/train-models", token=token)
        if train_models:
            df = pd.DataFrame(train_models)
            # Create assigned routes display column
            route_cols = ['r01', 'r02', 'r03', 'r04', 'r05', 'r06', 'r07', 'r08', 'r09']
            df['assigned_routes_display'] = df.apply(
                lambda row: ', '.join([col.upper() for col in route_cols if row.get(col)]),
                axis=1
            )
            
            table = dash_table.DataTable(
                data=df[['model_id', 'model_name', 'model_type', 'manufacturer', 'country_of_origin', 
                        'operational_units', 'assigned_routes_display']].to_dict('records'),
                columns=[
                    {'name': 'Model ID', 'id': 'model_id'},
                    {'name': 'Model Name', 'id': 'model_name'},
                    {'name': 'Type', 'id': 'model_type'},
                    {'name': 'Manufacturer', 'id': 'manufacturer'},
                    {'name': 'Country', 'id': 'country_of_origin'},
                    {'name': 'Units', 'id': 'operational_units'},
                    {'name': 'Assigned Routes', 'id': 'assigned_routes_display'},
                ],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '12px'},
                style_header={
                    'backgroundColor': COLORS['primary'],
                    'color': 'white',
                    'fontWeight': '600',
                    'border': 'none'
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}
                ]
            )
        else:
            table = html.P("No train models found", style={'textAlign': 'center', 'padding': '20px'})
        
        return (
            f"Train model '{model_name}' added successfully!", True, "success",
            "", "", "", "", "", None, None, None, None, None, None, [], table
        )
    else:
        error_msg = result.get('message', 'Failed to add train model') if isinstance(result, dict) else 'Failed to add train model'
        return error_msg, True, "danger", *([no_update] * 13)

@callback(
    [Output("ticket-count", "children"),
     Output("ticket-count-store", "data")],
    [Input("increase-tickets", "n_clicks"),
     Input("decrease-tickets", "n_clicks")],
    State("ticket-count-store", "data"),
    prevent_initial_call=True
)
def update_ticket_count(inc_clicks, dec_clicks, current_count):
    ctx = dash.callback_context
    if not ctx.triggered:
        return str(current_count), current_count
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "increase-tickets" and current_count < 10:
        new_count = current_count + 1
    elif button_id == "decrease-tickets" and current_count > 1:
        new_count = current_count - 1
    else:
        new_count = current_count
    return str(new_count), new_count
@callback(
    Output("passenger-details-container", "children"),
    Input("ticket-count-store", "data")
)
def update_passenger_fields(count):
    if not count or count < 1:
        return html.Div()
    passenger_fields = []
    for i in range(count):
        passenger_fields.append(
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H6(f"Passenger {i+1} Details", style={
                            'color': COLORS['text_primary'],
                            'fontWeight': '600',
                            'margin': '0'
                        })
                    ], width=6),
                    dbc.Col([
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-user", style={'marginRight': '6px'}),
                                "Adult"
                            ], id={"type": "passenger-type-btn-adult", "index": i}, style={
                                'background': COLORS['primary'],
                                'color': 'white',
                                'border': 'none',
                                'padding': '8px 16px',
                                'borderRadius': '8px 0 0 8px',
                                'cursor': 'pointer',
                                'fontSize': '13px',
                                'fontWeight': '500',
                                'transition': 'all 0.2s',
                                'flex': '1'
                            }),
                            html.Button([
                                html.I(className="fas fa-child", style={'marginRight': '6px'}),
                                "Child"
                            ], id={"type": "passenger-type-btn-child", "index": i}, style={
                                'background': '#e0e0e0',
                                'color': COLORS['text_secondary'],
                                'border': 'none',
                                'padding': '8px 16px',
                                'borderRadius': '0 8px 8px 0',
                                'cursor': 'pointer',
                                'fontSize': '13px',
                                'fontWeight': '500',
                                'transition': 'all 0.2s',
                                'flex': '1'
                            }),
                            dbc.RadioItems(
                                id={"type": "passenger-type", "index": i},
                                options=[
                                    {"label": " Adult", "value": "adult"},
                                    {"label": " Child", "value": "child"}
                                ],
                                value="adult",
                                inline=True,
                                style={'display': 'none'}
                            )
                        ], style={'display': 'flex', 'gap': '0'})
                    ], width=6, style={'textAlign': 'right'})
                ], style={
                    'marginTop': '16px',
                    'marginBottom': '12px',
                    'paddingTop': '12px',
                    'borderTop': f'1px solid {COLORS["border"]}' if i > 0 else 'none'
                }),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("NIC/Passport *", style={'fontWeight': '500', 'fontSize': '13px'}),
                            dbc.Input(
                                id={"type": "passenger-nic", "index": i},
                                placeholder="123456789V or AB1234567",
                                style={'borderRadius': '6px'}
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Contact Number", style={'fontWeight': '500', 'fontSize': '13px'}),
                            dbc.Input(
                                id={"type": "passenger-contact", "index": i},
                                placeholder="0712345678",
                                style={'borderRadius': '6px'}
                            ),
                        ], width=6),
                    ], className="mb-2")
                ], id={"type": "passenger-fields", "index": i})
            ])
        )
    return html.Div(passenger_fields)
# Remaining callbacks for modals, notifications, etc.
@callback(
    Output("profile-modal", "is_open"),
    [Input("profile-settings-btn", "n_clicks"),
     Input("close-profile-modal", "n_clicks"),
     Input("save-profile-btn", "n_clicks")],
    State("profile-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_profile_modal(open_clicks, close_clicks, save_clicks, is_open):
    return not is_open
@callback(
    Output("password-modal", "is_open"),
    [Input("change-password-btn", "n_clicks"),
     Input("close-password-modal", "n_clicks"),
     Input("save-password-btn", "n_clicks")],
    State("password-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_password_modal(open_clicks, close_clicks, save_clicks, is_open):
    return not is_open
# ============= TICKET VERIFICATION & CANCELLATION =============
@callback(
    [Output("cancel-ticket-alert", "children"),
     Output("cancel-ticket-alert", "is_open"),
     Output("cancel-ticket-alert", "color"),
     Output("ticket-details-display", "children"),
     Output("update-ticket-status-btn", "disabled"),
     Output("verified-ticket-store", "data")],
    Input("verify-ticket-btn", "n_clicks"),
    [State("cancel-ticket-id", "value"),
     State("cancel-nic-passport", "value"),
     State("token-store", "data")],
    prevent_initial_call=True
)
def verify_ticket_for_cancel(n, ticket_id, nic_passport, token):
    """Verify ticket by ID and NIC/Passport"""
    if not n or not token:
        return "", False, "danger", html.Div(), True, None
    if not ticket_id or not nic_passport:
        return "Please enter both Ticket ID and NIC/Passport", True, "warning", html.Div(), True, None
    # Fetch ticket from backend
    ticket = make_api_request(f"/tickets/{ticket_id}", token=token)
    if not ticket:
        return f"❌ Ticket {ticket_id} not found", True, "danger", html.Div(), True, None
    # Verify NIC/Passport matches (v2.0: separate fields)
    ticket_nic = ticket.get('nic')
    ticket_passport = ticket.get('passport')
    # Check if provided value matches either NIC or Passport
    if not (ticket_nic == nic_passport or ticket_passport == nic_passport):
        return "❌ NIC/Passport does not match ticket records", True, "danger", html.Div(), True, None
    # Display ticket details
    ticket_info = html.Div([
        html.Div([
            html.Strong("✅ Ticket Verified", style={'color': COLORS['success'], 'fontSize': '14px'}),
        ], style={'marginBottom': '12px'}),
        html.Div([
            html.P([html.Strong("Ticket ID: "), ticket.get('ticket_id')], style={'margin': '4px 0', 'fontSize': '13px'}),
            html.P([html.Strong("Route: "), f"Station {ticket.get('origin_station_id')} → Station {ticket.get('destination_station_id')}"],
                   style={'margin': '4px 0', 'fontSize': '13px'}),
            html.P([html.Strong("Schedule Date: "), str(ticket.get('schedule_date'))],
                   style={'margin': '4px 0', 'fontSize': '13px'}),
            html.P([html.Strong("Class: "), str(ticket.get('class'))],
                   style={'margin': '4px 0', 'fontSize': '13px'}),
            html.P([html.Strong("Fee: "), f"LKR {ticket.get('fee', 0)}"],
                   style={'margin': '4px 0', 'fontSize': '13px', 'fontWeight': '600', 'color': COLORS['primary']}),
            html.P([html.Strong("Current Status: "), str(ticket.get('status'))],
                   style={'margin': '4px 0', 'fontSize': '13px', 'color': COLORS['info']})
        ], style={
            'padding': '12px',
            'background': '#f8fafc',
            'borderRadius': '8px',
            'border': f'1px solid {COLORS["border"]}'
        })
    ])
    return "✅ Ticket verified successfully. You can now update the status.", True, "success", ticket_info, False, ticket
@callback(
    [Output("cancel-ticket-alert", "children", allow_duplicate=True),
     Output("cancel-ticket-alert", "is_open", allow_duplicate=True),
     Output("cancel-ticket-alert", "color", allow_duplicate=True),
     Output("cancel-ticket-id", "value"),
     Output("cancel-nic-passport", "value"),
     Output("cancel-ticket-status", "value"),
     Output("ticket-details-display", "children", allow_duplicate=True),
     Output("update-ticket-status-btn", "disabled", allow_duplicate=True)],
    Input("update-ticket-status-btn", "n_clicks"),
    [State("verified-ticket-store", "data"),
     State("cancel-ticket-status", "value"),
     State("token-store", "data")],
    prevent_initial_call=True
)
def update_ticket_status(n, verified_ticket, new_status, token):
    """Update ticket status (cancel/refund)"""
    if not n or not token:
        return "", False, "danger", no_update, no_update, no_update, no_update, no_update
    if not verified_ticket:
        return "⚠️ Please verify a ticket first", True, "warning", no_update, no_update, no_update, no_update, no_update
    if not new_status:
        return "⚠️ Please select a new status", True, "warning", no_update, no_update, no_update, no_update, no_update
    ticket_id = verified_ticket.get('ticket_id')
    # Update ticket status via backend API
    result = make_api_request(
        f"/tickets/{ticket_id}/status",
        method="PATCH",
        token=token,
        data={"status": new_status}
    )
    if result:
        return f"✅ Ticket {ticket_id} status updated to {new_status}", True, "success", "", "", None, html.Div(), True
    else:
        return f"❌ Failed to update ticket status", True, "danger", no_update, no_update, no_update, no_update, no_update
# ============= SCHEDULE BY STATION CALLBACKS =============
@callback(
    Output("schedule-origin-station", "options"),
    Input("url", "pathname"),
    prevent_initial_call=False
)
def load_schedule_origin_stations(pathname):
    """Load origin stations for schedule search"""
    if pathname != "/schedule-stations":
        return []

    # Stations endpoint doesn't require authentication
    stations = make_api_request("/stations", token=None)
    if stations and isinstance(stations, list):
        opts = [{"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")} for s in stations]
        return opts
    return []

@callback(
    Output("schedule-destination-station", "options"),
    [Input("url", "pathname"),
     Input("schedule-origin-station", "value")],
    prevent_initial_call=False
)
def load_schedule_destination_stations(pathname, origin_value):
    """Load destination stations for schedule search, excluding the selected origin"""
    if pathname != "/schedule-stations":
        return []

    stations = make_api_request("/stations", token=None)
    if stations and isinstance(stations, list):
        # Exclude the origin station from destination options
        opts = [
            {"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")}
            for s in stations
            if s.get("station_id") != origin_value
        ]
        return opts
    return []

@callback(
    [Output("schedule-results-container", "children"),
     Output("schedule-station-alert", "children"),
     Output("schedule-station-alert", "is_open"),
     Output("schedule-station-alert", "color")],
    Input("search-schedules-btn", "n_clicks"),
    [State("schedule-origin-station", "value"),
     State("schedule-destination-station", "value"),
     State("schedule-date-picker", "value"),
     State("token-store", "data")],
    prevent_initial_call=True
)
def search_schedules_by_station(n_clicks, origin, destination, date, token):
    """Search and display train schedules based on station and date selection"""
    if not n_clicks or not token:
        return html.Div(), "", False, "info"

    # Validate origin station is selected
    if not origin:
        return html.Div(), "Please select an origin station", True, "warning"

    if not date:
        return html.Div(), "Please select a date", True, "warning"

    # Build API endpoint based on selection
    if destination:
        # Both origin and destination selected
        endpoint = f"/schedules/search?origin_station_id={origin}&destination_station_id={destination}&schedule_date={date}"
    else:
        # Only origin selected - show all trains through that station
        endpoint = f"/schedules/by-station?station_id={origin}&schedule_date={date}"

    schedules = make_api_request(endpoint, token=token)

    if not schedules:
        return (
            dbc.Alert([
                html.I(className="fas fa-info-circle", style={'marginRight': '8px'}),
                "No train schedules found for the selected criteria."
            ], color="info"),
            "", False, "info"
        )

    # Display schedules in a formatted card layout
    schedule_cards = []

    for idx, schedule in enumerate(schedules):
        # Extract schedule information
        train_name = schedule.get('train_name', 'N/A')
        train_id = schedule.get('train_id', 'N/A')
        origin_station = schedule.get('origin_station', 'N/A')
        destination_station = schedule.get('destination_station', 'N/A')
        departure_time = schedule.get('departure_time', 'N/A')
        arrival_time = schedule.get('arrival_time', 'N/A')

        # Get available classes - this might be a list or comma-separated string
        available_classes = schedule.get('available_classes', [])
        if isinstance(available_classes, str):
            available_classes = [c.strip() for c in available_classes.split(',')]
        elif not isinstance(available_classes, list):
            available_classes = ['First', 'Second', 'Third']  # Default

        # Create class badges
        class_badges = []
        class_colors = {
            'First': COLORS['primary'],
            'Second': COLORS['info'],
            'Third': COLORS['success']
        }

        for cls in available_classes:
            class_badges.append(
                html.Span(cls, style={
                    'display': 'inline-block',
                    'padding': '4px 12px',
                    'background': class_colors.get(cls, COLORS['text_secondary']),
                    'color': 'white',
                    'borderRadius': '12px',
                    'fontSize': '11px',
                    'fontWeight': '600',
                    'marginRight': '6px',
                    'marginBottom': '4px'
                })
            )

        schedule_card = html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-train", style={
                            'fontSize': '32px',
                            'color': COLORS['primary']
                        })
                    ], style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'height': '100%'
                    })
                ], width=1),
                dbc.Col([
                    html.Div([
                        html.H5(train_name, style={
                            'margin': '0',
                            'color': COLORS['text_primary'],
                            'fontWeight': '600'
                        }),
                        html.P(f"Train ID: {train_id}", style={
                            'margin': '4px 0 0 0',
                            'fontSize': '12px',
                            'color': COLORS['text_secondary']
                        })
                    ])
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-map-marker-alt", style={
                                'color': COLORS['success'],
                                'marginRight': '6px'
                            }),
                            html.Strong("Origin: ", style={'fontSize': '13px'}),
                            html.Span(origin_station, style={'fontSize': '13px'})
                        ], style={'marginBottom': '4px'}),
                        html.Div([
                            html.I(className="fas fa-flag-checkered", style={
                                'color': COLORS['error'],
                                'marginRight': '6px'
                            }),
                            html.Strong("Destination: ", style={'fontSize': '13px'}),
                            html.Span(destination_station, style={'fontSize': '13px'})
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-clock", style={
                                'color': COLORS['info'],
                                'marginRight': '6px'
                            }),
                            html.Strong("Departure: ", style={'fontSize': '13px'}),
                            html.Span(departure_time, style={'fontSize': '13px', 'fontWeight': '600'})
                        ], style={'marginBottom': '4px'}),
                        html.Div([
                            html.I(className="fas fa-clock", style={
                                'color': COLORS['warning'],
                                'marginRight': '6px'
                            }),
                            html.Strong("Arrival: ", style={'fontSize': '13px'}),
                            html.Span(arrival_time, style={'fontSize': '13px', 'fontWeight': '600'})
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.P("Available Classes:", style={
                            'margin': '0 0 6px 0',
                            'fontSize': '12px',
                            'fontWeight': '600',
                            'color': COLORS['text_secondary']
                        }),
                        html.Div(class_badges, style={'display': 'flex', 'flexWrap': 'wrap'})
                    ])
                ], width=2),
            ])
        ], style={
            'background': COLORS['surface'],
            'padding': '20px',
            'borderRadius': '12px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
            'border': f'1px solid {COLORS["border"]}',
            'marginBottom': '16px',
            'transition': 'all 0.3s ease'
        }, className="schedule-card")

        schedule_cards.append(schedule_card)

    # Add summary header
    results_content = html.Div([
        html.Div([
            html.H5(f"Found {len(schedules)} train schedule(s)", style={
                'color': COLORS['text_primary'],
                'fontWeight': '600',
                'marginBottom': '16px'
            }),
        ]),
        html.Div(schedule_cards)
    ])

    return results_content, f"Found {len(schedules)} schedules", True, "success"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)