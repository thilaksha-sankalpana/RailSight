"""
TCDAFS - Global Search Callbacks
Handle global search functionality across schedules, trains, routes, and stations
"""
from dash import callback, Input, Output, State, html, no_update
from utils.api import make_api_request
from config.styles import COLORS
import logging

logger = logging.getLogger(__name__)


def register(app):
    """Register search callbacks with the app"""

    @callback(
        [Output("search-results", "children"),
         Output("search-results", "style")],
        Input("global-search", "value"),
        State("token-store", "data"),
        prevent_initial_call=True
    )
    def update_search_results(search_query, token):
        """
        Perform global search across schedules, trains, routes, and stations

        Args:
            search_query: Search input value
            token: Authentication token data

        Returns:
            Tuple of (search_results_content, search_results_style)
        """
        # If search is empty or too short, hide results
        if not search_query or len(search_query) < 2:
            return [], {'display': 'none'}

        if not token:
            return [], {'display': 'none'}

        search_query_lower = search_query.lower().strip()
        results = []
        
        # Show loading state
        loading_style = {
            'position': 'absolute',
            'top': '100%',
            'left': 0,
            'right': 0,
            'background': 'white',
            'boxShadow': '0 8px 32px rgba(0,0,0,0.15)',
            'borderRadius': '12px',
            'marginTop': '8px',
            'maxHeight': '500px',
            'overflowY': 'auto',
            'display': 'block',
            'zIndex': 1000,
            'border': f'1px solid {COLORS["border"]}'
        }
        
        try:
            logger.info(f"🔍 Searching for: '{search_query}'")
            
            # Search trains
            logger.info("Fetching trains data...")
            trains_data = make_api_request("/trains", token=token, timeout=10)
            logger.info(f"Trains data received: {len(trains_data) if trains_data else 0} items")
            if trains_data and isinstance(trains_data, list):
                matching_trains = [
                    t for t in trains_data 
                    if search_query_lower in t.get('train_id', '').lower() or
                       search_query_lower in t.get('model_id', '').lower()
                ][:5]
                
                if matching_trains:
                    results.append(html.Div([
                        html.H6("🚂 Trains", style={
                            'margin': '0 0 8px 0',
                            'padding': '12px 16px 8px 16px',
                            'fontSize': '13px',
                            'fontWeight': '600',
                            'color': COLORS['text_secondary'],
                            'borderBottom': f'1px solid {COLORS["border"]}'
                        }),
                        html.Div([
                            html.A([
                                html.I(className="fas fa-train", style={
                                    'marginRight': '10px',
                                    'color': COLORS['primary'],
                                    'fontSize': '14px'
                                }),
                                html.Span(t['train_id'], style={'fontWeight': '500'}),
                                html.Span(f" - {t.get('model_id', 'N/A')}", style={
                                    'color': COLORS['text_secondary'],
                                    'fontSize': '13px',
                                    'marginLeft': '8px'
                                })
                            ], href="/trains", style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'padding': '10px 16px',
                                'textDecoration': 'none',
                                'color': COLORS['text_primary'],
                                'transition': 'background 0.2s ease',
                                'borderRadius': '6px'
                            }, className="search-result-item")
                            for t in matching_trains
                        ])
                    ]))

            # Search schedules
            logger.info("Fetching schedules data...")
            schedules_data = make_api_request("/schedules", token=token, timeout=10)
            logger.info(f"Schedules data received: {len(schedules_data) if schedules_data else 0} items")
            if schedules_data and isinstance(schedules_data, list):
                matching_schedules = [
                    s for s in schedules_data 
                    if search_query_lower in s.get('train_schedule_id', '').lower() or
                       search_query_lower in s.get('train_schedule', '').lower() or
                       search_query_lower in s.get('route_id', '').lower() or
                       search_query_lower in s.get('train_id', '').lower()
                ][:5]
                
                if matching_schedules:
                    results.append(html.Div([
                        html.H6("📅 Schedules", style={
                            'margin': '0 0 8px 0',
                            'padding': '12px 16px 8px 16px',
                            'fontSize': '13px',
                            'fontWeight': '600',
                            'color': COLORS['text_secondary'],
                            'borderBottom': f'1px solid {COLORS["border"]}'
                        }),
                        html.Div([
                            html.A([
                                html.I(className="fas fa-calendar-alt", style={
                                    'marginRight': '10px',
                                    'color': COLORS['info'],
                                    'fontSize': '14px'
                                }),
                                html.Span(s['train_schedule'], style={'fontWeight': '500'}),
                                html.Span(f" ({s['train_schedule_id']})", style={
                                    'color': COLORS['text_secondary'],
                                    'fontSize': '13px',
                                    'marginLeft': '8px'
                                })
                            ], href="/schedules", style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'padding': '10px 16px',
                                'textDecoration': 'none',
                                'color': COLORS['text_primary'],
                                'transition': 'background 0.2s ease',
                                'borderRadius': '6px'
                            }, className="search-result-item")
                            for s in matching_schedules
                        ])
                    ]))

            # Search routes
            logger.info("Fetching routes data...")
            routes_data = make_api_request("/routes", token=token, timeout=10)
            logger.info(f"Routes data received: {len(routes_data) if routes_data else 0} items")
            if routes_data and isinstance(routes_data, list):
                matching_routes = [
                    r for r in routes_data 
                    if search_query_lower in r.get('route_id', '').lower() or
                       search_query_lower in r.get('route_name', '').lower()
                ][:5]
                
                if matching_routes:
                    results.append(html.Div([
                        html.H6("🗺️ Routes", style={
                            'margin': '0 0 8px 0',
                            'padding': '12px 16px 8px 16px',
                            'fontSize': '13px',
                            'fontWeight': '600',
                            'color': COLORS['text_secondary'],
                            'borderBottom': f'1px solid {COLORS["border"]}'
                        }),
                        html.Div([
                            html.A([
                                html.I(className="fas fa-route", style={
                                    'marginRight': '10px',
                                    'color': COLORS['success'],
                                    'fontSize': '14px'
                                }),
                                html.Span(r['route_name'], style={'fontWeight': '500'}),
                                html.Span(f" ({r['route_id']})", style={
                                    'color': COLORS['text_secondary'],
                                    'fontSize': '13px',
                                    'marginLeft': '8px'
                                })
                            ], href="/routes", style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'padding': '10px 16px',
                                'textDecoration': 'none',
                                'color': COLORS['text_primary'],
                                'transition': 'background 0.2s ease',
                                'borderRadius': '6px'
                            }, className="search-result-item")
                            for r in matching_routes
                        ])
                    ]))

            # Search stations
            logger.info("Fetching stations data...")
            stations_data = make_api_request("/stations", token=token, timeout=10)
            logger.info(f"Stations data received: {len(stations_data) if stations_data else 0} items")
            if stations_data and isinstance(stations_data, list):
                matching_stations = [
                    st for st in stations_data 
                    if search_query_lower in st.get('station_id', '').lower() or
                       search_query_lower in st.get('station_name', '').lower()
                ][:5]
                
                if matching_stations:
                    results.append(html.Div([
                        html.H6("🚉 Stations", style={
                            'margin': '0 0 8px 0',
                            'padding': '12px 16px 8px 16px',
                            'fontSize': '13px',
                            'fontWeight': '600',
                            'color': COLORS['text_secondary'],
                            'borderBottom': f'1px solid {COLORS["border"]}'
                        }),
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-map-marker-alt", style={
                                    'marginRight': '10px',
                                    'color': COLORS['warning'],
                                    'fontSize': '14px'
                                }),
                                html.Span(st['station_name'], style={'fontWeight': '500'}),
                                html.Span(f" ({st['station_id']})", style={
                                    'color': COLORS['text_secondary'],
                                    'fontSize': '13px',
                                    'marginLeft': '8px'
                                })
                            ], style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'padding': '10px 16px',
                                'color': COLORS['text_primary'],
                                'borderRadius': '6px'
                            })
                            for st in matching_stations
                        ])
                    ]))

            # If no results found
            if not results:
                logger.info(f"No results found for: '{search_query}'")
                results.append(html.Div([
                    html.I(className="fas fa-search", style={
                        'fontSize': '32px',
                        'color': COLORS['text_secondary'],
                        'marginBottom': '12px'
                    }),
                    html.P("No results found", style={
                        'color': COLORS['text_secondary'],
                        'margin': '0',
                        'fontSize': '14px'
                    })
                ], style={
                    'textAlign': 'center',
                    'padding': '40px 20px',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'alignItems': 'center',
                    'justifyContent': 'center'
                }))

        except Exception as e:
            logger.error(f"Search error: {e}")
            results.append(html.Div([
                html.I(className="fas fa-exclamation-triangle", style={
                    'fontSize': '24px',
                    'color': COLORS['error'],
                    'marginBottom': '8px'
                }),
                html.P("Error loading search results", style={
                    'color': COLORS['text_secondary'],
                    'margin': '0',
                    'fontSize': '13px'
                }),
                html.P(str(e), style={
                    'color': COLORS['text_secondary'],
                    'margin': '4px 0 0 0',
                    'fontSize': '11px',
                    'opacity': '0.7'
                })
            ], style={
                'textAlign': 'center',
                'padding': '30px 20px'
            }))

        # Show results
        return results, loading_style

