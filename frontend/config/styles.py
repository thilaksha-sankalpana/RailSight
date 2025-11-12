"""
TCDAFS - Styling Constants
Contains all color schemes and style configurations
"""

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

# ============= COMPONENT STYLES =============
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
    'fontFamily': 'Roboto, sans-serif',
    'borderTopRightRadius': '16px',
    'borderBottomRightRadius': '16px',
    'scrollbarWidth': 'none',  # Firefox
    'msOverflowStyle': 'none'  # IE and Edge
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
    'zIndex': 999,
    'borderBottomLeftRadius': '16px',
    'borderBottomRightRadius': '16px'
}

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
