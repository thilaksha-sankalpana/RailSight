"""
TCDAFS - Login Page Component
Authentication page with animated form
"""
from dash import html
import dash_bootstrap_components as dbc
from config.styles import COLORS, BUTTON_PRIMARY


def login_layout():
    """
    Create login page layout with form fields and animations

    Returns:
        Dash HTML component for the login page
    """
    return html.Div([
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

                # Login button with enhanced hover and click animations
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
