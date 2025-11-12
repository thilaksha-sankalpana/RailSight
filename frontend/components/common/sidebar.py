"""
TCDAFS - Sidebar Navigation Component
Main navigation sidebar with user profile and logout
"""
from dash import html, dcc
from config.styles import SIDEBAR_STYLE, NAV_LINK_STYLE, COLORS


def create_sidebar(username="User", email="user@railway.lk", full_name="Administrator", current_path="/"):
    """
    Create sidebar navigation with active route highlighting

    Args:
        username: User's username (deprecated, use email)
        email: User's email address
        full_name: User's full name
        current_path: Current active route path for highlighting

    Returns:
        Dash HTML component for the sidebar
    """
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
    ], id='sidebar', style=SIDEBAR_STYLE)
