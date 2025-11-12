"""
TCDAFS - Stat Card Component
Reusable dashboard statistic card component
"""
from dash import html
from config.styles import COLORS


def create_stat_card(icon, value, label, color):
    """
    Create a statistic card for dashboard

    Args:
        icon: Font Awesome icon class (e.g., "fas fa-train")
        value: The statistic value to display
        label: Description label for the stat
        color: Accent color for the icon background

    Returns:
        Dash HTML component for the stat card
    """
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
