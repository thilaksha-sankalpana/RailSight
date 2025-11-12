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
                html.I(className=icon, style={'fontSize': '34px', 'color': color}),
            ], style={
                'flex': '0 0 68px',
                'height': '68px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'background': f'{color}15',
                'borderRadius': '14px',
                'boxShadow': f'0 2px 8px {color}20'
            }),
            html.Div([
                html.H3(value, style={
                    'margin': '0',
                    'fontSize': '30px',
                    'fontWeight': '700',
                    'color': COLORS['text_primary'],
                    'letterSpacing': '-0.5px'
                }),
                html.P(label, style={
                    'margin': '0',
                    'color': COLORS['text_secondary'],
                    'fontSize': '14px',
                    'marginTop': '6px',
                    'fontWeight': '500',
                    'lineHeight': '1.3'
                })
            ], style={'marginLeft': '18px', 'flex': '1'})
        ], style={'display': 'flex', 'alignItems': 'center'})
    ], className="stat-card", style={
        'background': COLORS['surface'],
        'padding': '26px',
        'borderRadius': '14px',
        'boxShadow': '0 3px 12px rgba(0,0,0,0.09)',
        'border': f'1px solid {COLORS["border"]}',
        'transition': 'all 0.3s ease',
        'height': '100%'
    })
