"""
TCDAFS - Main Application Entry Point
Train Compartment Demand Analysis & Forecasting System
"""
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import logging

from config.settings import APP_CONFIG, EXTERNAL_STYLESHEETS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP] + EXTERNAL_STYLESHEETS,
    suppress_callback_exceptions=True,
    title=APP_CONFIG['title']
)

server = app.server
server.secret_key = APP_CONFIG['secret_key']

# Set custom favicon (train emoji)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🚂</text></svg>">
        {%css%}
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

# Main app layout
app.layout = html.Div([
    dcc.Store(id="token-store", storage_type="session"),
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

# Import and register callbacks
from callbacks import register_callbacks
register_callbacks(app)

if __name__ == "__main__":
    logger.info(f"Starting {APP_CONFIG['title']}...")
    logger.info(f"Running on http://{APP_CONFIG['host']}:{APP_CONFIG['port']}")
    app.run(
        debug=APP_CONFIG['debug'],
        host=APP_CONFIG['host'],
        port=APP_CONFIG['port']
    )
