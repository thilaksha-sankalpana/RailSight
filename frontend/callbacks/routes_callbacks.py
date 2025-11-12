"""
TCDAFS - Train Routes Callbacks
Handle train routes CRUD operations and table display
"""
from dash import callback, Input, Output, State, html, no_update, dash_table, callback_context, ALL
import pandas as pd
from utils.api import make_api_request
from utils.cache import get_cached
from config.styles import COLORS
import logging
import dash_bootstrap_components as dbc

logger = logging.getLogger(__name__)

print("routes_callbacks.py module loaded successfully")


def get_stations_initial():
    """Get initial list of stations (top 50) for quick loading"""
    def fetch_stations():
        stations = make_api_request("/stations?limit=50", token=None, timeout=15)
        logger.info(f"Fetched {len(stations) if stations else 0} initial stations from backend")
        return stations if (stations and isinstance(stations, list)) else []

    return get_cached("stations_initial", fetch_stations, ttl_minutes=10)


def search_stations(search_query):
    """Search stations by name with server-side filtering"""
    if not search_query or len(search_query) < 2:
        return get_stations_initial()

    stations = make_api_request(f"/stations?search={search_query}&limit=20", token=None, timeout=10)
    logger.info(f"Searched stations with query '{search_query}', found {len(stations) if stations else 0} results")
    return stations if (stations and isinstance(stations, list)) else []


def generate_next_route_id(token):
    """Generate next route ID in format R01, R02, etc."""
    try:
        # Fetch existing routes (max 500 per request due to API limit)
        all_routes = []
        skip = 0
        limit = 500

        while True:
            routes = make_api_request(f"/routes?skip={skip}&limit={limit}", token=token, timeout=10)
            if not routes or not isinstance(routes, list) or len(routes) == 0:
                break
            all_routes.extend(routes)
            if len(routes) < limit:
                # Got all routes
                break
            skip += limit

        if not all_routes:
            return "R01"

        # Extract numeric parts from route IDs that match R## pattern
        max_num = 0
        for route in all_routes:
            route_id = route.get("route_id", "")
            if route_id.startswith("R") and len(route_id) >= 2:
                try:
                    num = int(route_id[1:])
                    max_num = max(max_num, num)
                except ValueError:
                    continue

        # Generate next ID
        next_num = max_num + 1
        return f"R{next_num:02d}"  # Format as R01, R02, etc.
    except Exception as e:
        logger.error(f"Error generating route ID: {e}")
        # If error, try to find a safe ID by checking sequentially
        for i in range(1, 1000):
            test_id = f"R{i:02d}"
            # Check if this ID exists
            existing = make_api_request(f"/routes/{test_id}", token=token, timeout=5)
            if not existing:
                return test_id
        return "R999"  # Fallback


def register(app):
    """Register train routes callbacks with the app"""
    print("Registering routes callbacks...")

    @callback(
        Output("routes-table", "children"),
        [Input("url", "pathname"),
         Input("routes-refresh-trigger", "data")],
        [State("token-store", "data")],
        prevent_initial_call=False
    )
    def load_routes(pathname, refresh_trigger, token):
        """Load and display routes table with modern UI"""
        if pathname != "/routes" or not token:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-spinner fa-spin", style={
                        'fontSize': '32px',
                        'color': COLORS['primary'],
                        'marginBottom': '12px'
                    }),
                    html.P("Loading routes...", style={
                        'color': COLORS['text_secondary'],
                        'fontSize': '15px',
                        'fontWeight': '500'
                    })
                ], style={
                    'textAlign': 'center',
                    'padding': '60px 20px'
                })
            ])

        routes = make_api_request("/routes", token=token)

        if not routes:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-route", style={
                        'fontSize': '64px',
                        'color': COLORS['text_secondary'],
                        'opacity': '0.3',
                        'marginBottom': '20px'
                    }),
                    html.H5("No Routes Configured", style={
                        'color': COLORS['text_primary'],
                        'fontWeight': '700',
                        'marginBottom': '8px',
                        'fontSize': '20px'
                    }),
                    html.P("Get started by creating your first railway route", style={
                        'color': COLORS['text_secondary'],
                        'fontSize': '15px',
                        'marginBottom': '24px'
                    }),
                    dbc.Button([
                        html.I(className="fas fa-plus-circle", style={'marginRight': '8px'}),
                        "Create First Route"
                    ], color="primary", size="lg", style={
                        'borderRadius': '10px',
                        'padding': '12px 28px',
                        'fontWeight': '600',
                        'boxShadow': '0 4px 12px rgba(37, 99, 235, 0.3)'
                    }, href="#", id={"type": "add-route-btn-alt", "index": 0})
                ], style={
                    'textAlign': 'center',
                    'padding': '80px 20px'
                })
            ])

        # Create modern table rows
        table_rows = []

        for idx, route in enumerate(routes):
            row_style = {
                'borderBottom': f'1px solid {COLORS["border"]}',
                'padding': '20px 24px',
                'transition': 'all 0.2s ease',
                'background': '#ffffff' if idx % 2 == 0 else '#fafbfc'
            }

            table_rows.append(
                html.Div([
                    # Route ID Badge
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-hashtag", style={
                                'fontSize': '10px',
                                'marginRight': '6px',
                                'opacity': '0.7'
                            }),
                            html.Span(route.get('route_id', 'N/A'), style={
                                'fontWeight': '700',
                                'fontSize': '14px'
                            })
                        ], style={
                            'background': f'{COLORS["primary"]}15',
                            'color': COLORS['primary'],
                            'padding': '8px 16px',
                            'borderRadius': '8px',
                            'display': 'inline-flex',
                            'alignItems': 'center',
                            'fontWeight': '600',
                            'fontSize': '13px',
                            'border': f'1px solid {COLORS["primary"]}30'
                        })
                    ], style={'flex': '0 0 120px'}),

                    # Route Name
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-route", style={
                                'marginRight': '10px',
                                'color': COLORS['primary'],
                                'fontSize': '14px'
                            }),
                            html.Span(route.get('route_name', 'Unnamed Route'), style={
                                'fontWeight': '600',
                                'fontSize': '15px',
                                'color': COLORS['text_primary']
                            })
                        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '6px'}),
                        html.Div([
                            html.I(className="fas fa-map-marked-alt", style={
                                'marginRight': '8px',
                                'color': COLORS['text_secondary'],
                                'fontSize': '12px'
                            }),
                            html.Span(route.get('route', 'No description'), style={
                                'fontSize': '13px',
                                'color': COLORS['text_secondary']
                            })
                        ], style={'display': 'flex', 'alignItems': 'center'})
                    ], style={'flex': '1', 'minWidth': '0'}),

                    # Action Buttons
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-edit", style={'marginRight': '8px', 'fontSize': '13px'}),
                            "Edit"
                        ], id={"type": "edit-route-btn", "index": route['route_id']},
                           size="sm",
                           color="primary",
                           outline=True,
                           style={
                               'marginRight': '10px',
                               'borderRadius': '8px',
                               'padding': '8px 16px',
                               'fontWeight': '600',
                               'fontSize': '13px',
                               'transition': 'all 0.2s ease'
                           }),
                        dbc.Button([
                            html.I(className="fas fa-trash-alt", style={'marginRight': '8px', 'fontSize': '13px'}),
                            "Delete"
                        ], id={"type": "delete-route-btn", "index": route['route_id']},
                           size="sm",
                           color="danger",
                           outline=True,
                           style={
                               'borderRadius': '8px',
                               'padding': '8px 16px',
                               'fontWeight': '600',
                               'fontSize': '13px',
                               'transition': 'all 0.2s ease'
                           }),
                    ], style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'flex': '0 0 auto'
                    })
                ], style={
                    **row_style,
                    'display': 'flex',
                    'alignItems': 'center',
                    'gap': '20px',
                    'cursor': 'pointer'
                }, className='route-row')
            )

        # Summary header
        summary = html.Div([
            html.Div([
                html.I(className="fas fa-info-circle", style={
                    'marginRight': '8px',
                    'color': COLORS['primary'],
                    'fontSize': '14px'
                }),
                html.Span(f"Showing {len(routes)} route{'s' if len(routes) != 1 else ''}", style={
                    'fontSize': '14px',
                    'color': COLORS['text_secondary'],
                    'fontWeight': '500'
                })
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'padding': '12px 24px',
            'background': '#f8f9fa',
            'borderBottom': f'2px solid {COLORS["border"]}',
            'borderRadius': '12px 12px 0 0'
        })

        return html.Div([
            summary,
            html.Div(table_rows, style={
                'background': '#ffffff',
                'borderRadius': '0 0 12px 12px',
                'overflow': 'hidden'
            })
        ], style={
            'borderRadius': '12px',
            'overflow': 'hidden',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.05)'
        })

    @callback(
        [Output("route-modal", "is_open"),
         Output("route-modal-title", "children"),
         Output("route-name", "value"),
         Output("route-origin", "value"),
         Output("route-destination", "value"),
         Output("route-distance", "value"),
         Output("route-duration", "value"),
         Output("route-edit-id", "data")],
        [Input("add-route-btn", "n_clicks"),
         Input({"type": "edit-route-btn", "index": ALL}, "n_clicks"),
         Input("cancel-route-btn", "n_clicks"),
         Input("save-route-btn", "n_clicks")],
        [State("route-modal", "is_open"),
         State("route-edit-id", "data"),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def toggle_route_modal(add_clicks, edit_clicks, cancel_clicks, save_clicks,
                          is_open, edit_id, token):
        """Handle route modal open/close and populate for editing"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update

        triggered_id = ctx.triggered[0]["prop_id"]

        # Ignore if triggered by None values (initial load)
        if ctx.triggered[0]["value"] is None:
            return no_update

        # Close modal
        if "cancel" in triggered_id or "save" in triggered_id:
            return False, "", "", None, None, "", "", None

        # Open for adding new route
        if "add-route-btn" in triggered_id:
            return True, "Add New Route", "", None, None, "", "", None

        # Open for editing
        if "edit-route-btn" in triggered_id:
            # Find which button was clicked
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            route_id = eval(button_id)["index"]

            # Fetch route data
            route = make_api_request(f"/routes/{route_id}", token=token)
            if route:
                return (True, f"Edit Route: {route['route_name']}",
                       route['route_name'], None, None, "", "", route_id)

        return no_update

    @callback(
        Output("route-origin", "options"),
        [Input("route-modal", "is_open"),
         Input("route-origin", "search_value")],
        [State("token-store", "data"),
         State("route-origin", "value")],
        prevent_initial_call=False
    )
    def load_route_origin_stations(is_open, search_value, token, current_value):
        """Load stations for origin dropdown with server-side search"""
        if not is_open:
            return []

        try:
            # Use server-side search if user is typing
            if search_value and len(search_value) >= 2:
                stations = search_stations(search_value)
                logger.info(f"Route origin search '{search_value}': got {len(stations) if stations else 0} stations")
            else:
                # Load initial 50 stations for fast load
                stations = get_stations_initial()
                logger.info(f"Route origin initial load: got {len(stations) if stations else 0} stations")

            if not stations or not isinstance(stations, list):
                logger.warning(f"No valid stations data received for route origin dropdown")
                return []

            opts = [{"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")} for s in stations]

            # If there's a current selection not in the new options, fetch and add it
            if current_value:
                existing_values = [opt["value"] for opt in opts]
                if current_value not in existing_values:
                    selected_station = make_api_request(f"/stations/{current_value}", token=None, timeout=5)
                    if selected_station and isinstance(selected_station, dict):
                        opts.insert(0, {"label": selected_station.get("station_name", "Unknown"),
                                       "value": selected_station.get("station_id", "")})
                        logger.info(f"Added current selection {current_value} to route origin options")

            logger.info(f"Returning {len(opts)} options for route origin dropdown")
            return opts
        except Exception as e:
            logger.error(f"Error in load_route_origin_stations: {e}", exc_info=True)
            return []

    @callback(
        Output("route-destination", "options"),
        [Input("route-modal", "is_open"),
         Input("route-origin", "value"),
         Input("route-destination", "search_value")],
        [State("token-store", "data"),
         State("route-destination", "value")],
        prevent_initial_call=False
    )
    def load_route_destination_stations(is_open, origin_value, search_value, token, current_value):
        """Load destination stations with server-side search, excluding the selected origin"""
        if not is_open:
            return []

        try:
            # Use server-side search if user is typing
            if search_value and len(search_value) >= 2:
                stations = search_stations(search_value)
                logger.info(f"Route destination search '{search_value}': got {len(stations) if stations else 0} stations")
            else:
                # Load initial 50 stations for fast load
                stations = get_stations_initial()
                logger.info(f"Route destination initial load: got {len(stations) if stations else 0} stations")

            if not stations or not isinstance(stations, list):
                logger.warning(f"No valid stations data received for route destination dropdown")
                return []

            # Exclude the origin station from destination options
            opts = [
                {"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")}
                for s in stations
                if s.get("station_id") != origin_value
            ]

            # If there's a current selection not in the new options, fetch and add it
            if current_value and current_value != origin_value:
                existing_values = [opt["value"] for opt in opts]
                if current_value not in existing_values:
                    selected_station = make_api_request(f"/stations/{current_value}", token=None, timeout=5)
                    if selected_station and isinstance(selected_station, dict):
                        opts.insert(0, {"label": selected_station.get("station_name", "Unknown"),
                                       "value": selected_station.get("station_id", "")})
                        logger.info(f"Added current selection {current_value} to route destination options")

            logger.info(f"Returning {len(opts)} options for route destination dropdown")
            return opts
        except Exception as e:
            logger.error(f"Error in load_route_destination_stations: {e}", exc_info=True)
            return []

    @callback(
        [Output("routes-refresh-trigger", "data"),
         Output("route-alert", "children"),
         Output("route-alert", "color"),
         Output("route-alert", "is_open")],
        [Input("save-route-btn", "n_clicks")],
        [State("route-name", "value"),
         State("route-origin", "value"),
         State("route-destination", "value"),
         State("route-distance", "value"),
         State("route-duration", "value"),
         State("route-edit-id", "data"),
         State("token-store", "data"),
         State("routes-refresh-trigger", "data")],
        prevent_initial_call=True
    )
    def save_route(n_clicks, route_name, origin, destination, distance, duration,
                  edit_id, token, current_trigger):
        """Save new or updated route"""
        if not n_clicks or not token:
            return no_update, no_update, no_update, no_update

        # Validate inputs
        if not route_name:
            return no_update, "Route name is required", "danger", True

        # Note: Current schema expects route_id and route description
        # This is a simplified version - you may need to adjust based on actual requirements
        try:
            # Fetch station names if origin and destination are provided
            origin_name = None
            destination_name = None

            if origin:
                origin_station = make_api_request(f"/stations/{origin}", token=token, timeout=5)
                if origin_station and isinstance(origin_station, dict):
                    origin_name = origin_station.get("station_name", origin)
                else:
                    origin_name = origin

            if destination:
                destination_station = make_api_request(f"/stations/{destination}", token=token, timeout=5)
                if destination_station and isinstance(destination_station, dict):
                    destination_name = destination_station.get("station_name", destination)
                else:
                    destination_name = destination

            # Build route description with station names
            if origin_name and destination_name:
                route_description = f"{origin_name} to {destination_name}"
            else:
                route_description = route_name

            if edit_id:
                # Update existing route
                data = {
                    "route_name": route_name,
                    "route": route_description
                }
                response = make_api_request(
                    f"/routes/{edit_id}",
                    method="PATCH",
                    data=data,
                    token=token
                )
                message = "Route updated successfully!"
            else:
                # Create new route - generate route_id in format R01, R02, etc.
                route_id = generate_next_route_id(token)

                data = {
                    "route_id": route_id,
                    "route_name": route_name,
                    "route": route_description
                }
                response = make_api_request(
                    "/routes",
                    method="POST",
                    data=data,
                    token=token
                )
                message = f"Route created successfully with ID: {route_id}"

            if response:
                return (current_trigger or 0) + 1, message, "success", True
            else:
                return no_update, "Failed to save route", "danger", True

        except Exception as e:
            logger.error(f"Error saving route: {e}")
            return no_update, f"Error: {str(e)}", "danger", True

    @callback(
        [Output("route-delete-modal", "is_open"),
         Output("route-delete-name", "children"),
         Output("route-delete-id", "data")],
        [Input({"type": "delete-route-btn", "index": ALL}, "n_clicks"),
         Input("cancel-delete-route-btn", "n_clicks"),
         Input("confirm-delete-route-btn", "n_clicks")],
        [State("route-delete-modal", "is_open"),
         State("route-delete-id", "data"),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def toggle_delete_modal(delete_clicks, cancel_clicks, confirm_clicks,
                           is_open, delete_id, token):
        """Handle delete confirmation modal"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update

        triggered_id = ctx.triggered[0]["prop_id"]

        # Ignore if triggered by None values (initial load)
        if ctx.triggered[0]["value"] is None:
            return no_update

        # Close modal
        if "cancel" in triggered_id or "confirm" in triggered_id:
            return False, "", None

        # Open delete modal
        if "delete-route-btn" in triggered_id:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            route_id = eval(button_id)["index"]

            # Fetch route name
            route = make_api_request(f"/routes/{route_id}", token=token)
            if route:
                return True, route['route_name'], route_id

        return no_update

    @callback(
        [Output("routes-refresh-trigger", "data", allow_duplicate=True),
         Output("route-alert", "children", allow_duplicate=True),
         Output("route-alert", "color", allow_duplicate=True),
         Output("route-alert", "is_open", allow_duplicate=True)],
        [Input("confirm-delete-route-btn", "n_clicks")],
        [State("route-delete-id", "data"),
         State("token-store", "data"),
         State("routes-refresh-trigger", "data")],
        prevent_initial_call=True
    )
    def delete_route(n_clicks, route_id, token, current_trigger):
        """Delete route"""
        if not n_clicks or not route_id or not token:
            return no_update, no_update, no_update, no_update

        try:
            response = make_api_request(
                f"/routes/{route_id}",
                method="DELETE",
                token=token
            )
            return (current_trigger or 0) + 1, "Route deleted successfully!", "success", True
        except Exception as e:
            logger.error(f"Error deleting route: {e}")
            return no_update, f"Error deleting route: {str(e)}", "danger", True

    # Add Store component for refresh trigger
    @callback(
        Output("routes-refresh-trigger", "data", allow_duplicate=True),
        [Input("url", "pathname")],
        prevent_initial_call=True
    )
    def init_refresh_trigger(pathname):
        """Initialize refresh trigger when page loads"""
        if pathname == "/routes":
            return 0
        return no_update

    print("Routes callbacks registered successfully")
