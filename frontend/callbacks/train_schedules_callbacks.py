"""
TCDAFS - Train Schedules Callbacks
Handle train schedules display with day-based filtering
"""
from dash import callback, Input, Output, State, html, no_update, callback_context, ALL
from utils.api import make_api_request
from utils.cache import get_cached
from config.styles import COLORS, BUTTON_PRIMARY
import logging
import dash_bootstrap_components as dbc
from datetime import datetime, date

logger = logging.getLogger(__name__)


def get_stations_initial():
    """Get initial list of stations (top 50) for quick loading"""
    def fetch_stations():
        # Load only first 50 stations for initial dropdown - much faster!
        stations = make_api_request("/stations?limit=50", token=None, timeout=15)
        logger.info(f"Fetched {len(stations) if stations else 0} initial stations from backend")
        return stations if (stations and isinstance(stations, list)) else []
    
    return get_cached("stations_initial", fetch_stations, ttl_minutes=10)


def search_stations(search_query):
    """Search stations by name with server-side filtering"""
    if not search_query or len(search_query) < 2:
        # If no search or too short, return initial list
        return get_stations_initial()
    
    # Search on backend with query - only returns matching stations
    stations = make_api_request(f"/stations?search={search_query}&limit=20", token=None, timeout=10)
    logger.info(f"Searched stations with query '{search_query}', found {len(stations) if stations else 0} results")
    return stations if (stations and isinstance(stations, list)) else []


def generate_next_schedule_id(token):
    """Generate next schedule ID in format SCH1001, SCH1002, etc."""
    try:
        # Fetch existing schedules (max 500 per request due to API limit)
        all_schedules = []
        skip = 0
        limit = 500

        while True:
            schedules = make_api_request(f"/schedules?skip={skip}&limit={limit}", token=token, timeout=10)
            if not schedules or not isinstance(schedules, list) or len(schedules) == 0:
                break
            all_schedules.extend(schedules)
            if len(schedules) < limit:
                # Got all schedules
                break
            skip += limit

        if not all_schedules:
            return "SCH1001"

        # Extract numeric parts from schedule IDs that match SCH#### pattern
        max_num = 1000
        for schedule in all_schedules:
            schedule_id = schedule.get("train_schedule_id", "")
            if schedule_id.startswith("SCH") and len(schedule_id) >= 4:
                try:
                    num = int(schedule_id[3:])
                    max_num = max(max_num, num)
                except ValueError:
                    continue

        # Generate next ID
        next_num = max_num + 1
        return f"SCH{next_num}"  # Format as SCH1001, SCH1002, etc.
    except Exception as e:
        logger.error(f"Error generating schedule ID: {e}")
        # If error, try to find a safe ID by checking sequentially
        for i in range(1001, 9999):
            test_id = f"SCH{i}"
            # Check if this ID exists
            existing = make_api_request(f"/schedules/{test_id}", token=token, timeout=5)
            if not existing:
                return test_id
        return "SCH9999"  # Fallback


def get_day_of_week(target_date):
    """
    Get day of week for a given date
    Backend handles poya/holiday filtering via the calendar service
    """
    return target_date.strftime("%A").lower()


def register(app):
    """Register train schedules callbacks with the app"""
    
    @callback(
        [Output("train-schedules-table", "children"),
         Output("schedule-count-badge", "children")],
        [Input("url", "pathname"),
         Input("apply-train-schedule-filter", "n_clicks"),
         Input("clear-train-schedule-filters", "n_clicks"),
         Input("train-schedule-alert", "is_open")],
        [State("filter-train-schedule-date", "value"),
         State("filter-train-schedule-origin", "value"),
         State("filter-train-schedule-destination", "value"),
         State("token-store", "data")],
        prevent_initial_call=False
    )
    def load_train_schedules(pathname, apply_clicks, clear_clicks, alert_open, 
                            filter_date, filter_origin, filter_destination, token):
        """Load and display train schedules table filtered by date and stations"""
        if pathname != "/schedules" or not token:
            return (html.Div([
                html.Div([
                    html.I(className="fas fa-spinner fa-spin", style={
                        'fontSize': '32px',
                        'color': COLORS['primary'],
                        'marginBottom': '12px'
                    }),
                    html.P("Loading schedules...", style={
                        'color': COLORS['text_secondary'],
                        'fontSize': '15px',
                        'fontWeight': '500'
                    })
                ], style={
                    'textAlign': 'center',
                    'padding': '60px 20px'
                })
            ]), "Loading...")

        # Determine which date to use
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
        
        # If clear button clicked, use today's date
        if triggered_id == "clear-train-schedule-filters":
            target_date = date.today()
        elif filter_date:
            try:
                target_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
            except:
                target_date = date.today()
        else:
            target_date = date.today()

        # Get day of week (backend handles poya/holiday filtering)
        day_of_week = get_day_of_week(target_date)

        logger.info(f"Loading schedules for {target_date} ({day_of_week})")

        # Use the schedules/by-date endpoint which handles day/poya/holiday filtering on backend
        # This is the dedicated endpoint for Train Schedules tab
        api_url = f"/schedules/by-date?schedule_date={target_date}&limit=500"

        # Add station filters if provided
        if filter_origin:
            api_url += f"&origin_station_id={filter_origin}"
        if filter_destination:
            api_url += f"&destination_station_id={filter_destination}"

        schedules = make_api_request(api_url, token=token, timeout=30)

        # Check if response is invalid (None or not a list)
        if schedules is None or not isinstance(schedules, list):
            logger.error(f"Invalid API response - expected list, got {type(schedules)}")
            return (html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle", style={
                        'fontSize': '64px',
                        'color': COLORS['danger'],
                        'opacity': '0.5',
                        'marginBottom': '20px'
                    }),
                    html.H5("Error Loading Schedules", style={
                        'color': COLORS['text_primary'],
                        'fontWeight': '700',
                        'marginBottom': '8px',
                        'fontSize': '20px'
                    }),
                    html.P("Failed to connect to the server. Please try again.", style={
                        'color': COLORS['text_secondary'],
                        'fontSize': '15px',
                        'marginBottom': '24px'
                    })
                ], style={
                    'textAlign': 'center',
                    'padding': '80px 20px'
                })
            ]), "0")

        # Backend already filtered by date, poya, holiday, and stations
        # So we can use the schedules directly
        filtered_schedules = schedules
        logger.info(f"Received {len(filtered_schedules)} schedules from backend for {target_date}")

        if not filtered_schedules:
            day_label = day_of_week.capitalize()

            # Determine the message based on whether filters were applied
            if filter_origin or filter_destination:
                message_title = f"No Schedules Match Your Filters"
                message_body = f"No trains found on {target_date.strftime('%B %d, %Y')} for the selected route"
            else:
                message_title = f"No Schedules for {day_label}"
                message_body = f"No trains are scheduled to operate on {target_date.strftime('%B %d, %Y')}"

            return (html.Div([
                html.Div([
                    html.I(className="fas fa-calendar-times", style={
                        'fontSize': '64px',
                        'color': COLORS['text_secondary'],
                        'opacity': '0.3',
                        'marginBottom': '20px'
                    }),
                    html.H5(message_title, style={
                        'color': COLORS['text_primary'],
                        'fontWeight': '700',
                        'marginBottom': '8px',
                        'fontSize': '20px'
                    }),
                    html.P(message_body, style={
                        'color': COLORS['text_secondary'],
                        'fontSize': '15px',
                        'marginBottom': '16px'
                    }),
                    dbc.Button([
                        html.I(className="fas fa-redo", style={'marginRight': '8px'}),
                        "Clear Filters"
                    ], id="clear-train-schedule-filters", color="primary", outline=True)
                ], style={
                    'textAlign': 'center',
                    'padding': '80px 20px'
                })
            ]), "0")

        # Create modern table rows
        table_rows = []

        for idx, schedule in enumerate(filtered_schedules):
            row_style = {
                'borderBottom': f'1px solid {COLORS["border"]}',
                'padding': '20px 24px',
                'transition': 'all 0.2s ease',
                'background': '#ffffff' if idx % 2 == 0 else '#fafbfc'
            }

            # Format times
            origin_departure = schedule.get('origin_departure', 'N/A')
            if origin_departure and origin_departure != 'N/A':
                try:
                    if 'T' in str(origin_departure):
                        origin_departure = datetime.fromisoformat(str(origin_departure).replace('Z', '+00:00')).strftime('%H:%M')
                    else:
                        origin_departure = str(origin_departure)[:5]
                except:
                    pass

            destination_arrival = schedule.get('destination_departure', 'N/A')
            if destination_arrival and destination_arrival != 'N/A':
                try:
                    if 'T' in str(destination_arrival):
                        destination_arrival = datetime.fromisoformat(str(destination_arrival).replace('Z', '+00:00')).strftime('%H:%M')
                    else:
                        destination_arrival = str(destination_arrival)[:5]
                except:
                    pass

            # Status badge colors
            status = schedule.get('status', 'Active')
            status_colors = {
                'Active': {'bg': '#10b98120', 'color': '#059669', 'icon': 'check-circle'},
                'Inactive': {'bg': '#ef444420', 'color': '#dc2626', 'icon': 'times-circle'},
                'Cancelled': {'bg': '#f5971520', 'color': '#f59e0b', 'icon': 'ban'},
                'Delayed': {'bg': '#f5971520', 'color': '#f59e0b', 'icon': 'clock'},
            }
            status_style = status_colors.get(status, status_colors['Active'])

            # Get station names
            origin_station = schedule.get('origin_station', schedule.get('origin_station_id', 'N/A'))
            destination_station = schedule.get('destination_station', schedule.get('destination_station_id', 'N/A'))

            table_rows.append(
                html.Div([
                    # Schedule ID Badge
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-hashtag", style={
                                'fontSize': '10px',
                                'marginRight': '6px',
                                'opacity': '0.7'
                            }),
                            html.Span(schedule.get('train_schedule_id', 'N/A'), style={
                                'fontWeight': '700',
                                'fontSize': '13px'
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
                    ], style={'flex': '0 0 140px'}),

                    # Schedule Details
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-train", style={
                                'marginRight': '10px',
                                'color': COLORS['primary'],
                                'fontSize': '14px'
                            }),
                            html.Span(schedule.get('train_schedule', 'Unnamed Schedule'), style={
                                'fontWeight': '600',
                                'fontSize': '15px',
                                'color': COLORS['text_primary']
                            })
                        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '6px'}),
                        html.Div([
                            html.Span([
                                html.I(className="fas fa-route", style={
                                    'marginRight': '6px',
                                    'color': COLORS['text_secondary'],
                                    'fontSize': '12px'
                                }),
                                html.Span(f"Route: {schedule.get('route_id', 'N/A')}", style={
                                    'fontSize': '13px',
                                    'color': COLORS['text_secondary']
                                })
                            ])
                        ])
                    ], style={'flex': '1', 'minWidth': '0'}),

                    # Route Details
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-map-marker-alt", style={
                                'marginRight': '6px',
                                'color': '#059669',
                                'fontSize': '12px'
                            }),
                            html.Span(origin_station, style={
                                'fontSize': '13px',
                                'fontWeight': '500',
                                'color': COLORS['text_primary']
                            })
                        ], style={'marginBottom': '4px'}),
                        html.Div([
                            html.I(className="fas fa-arrow-down", style={
                                'marginRight': '6px',
                                'color': COLORS['text_secondary'],
                                'fontSize': '10px'
                            }),
                        ], style={'marginBottom': '4px', 'marginLeft': '6px'}),
                        html.Div([
                            html.I(className="fas fa-map-marker-alt", style={
                                'marginRight': '6px',
                                'color': '#dc2626',
                                'fontSize': '12px'
                            }),
                            html.Span(destination_station, style={
                                'fontSize': '13px',
                                'fontWeight': '500',
                                'color': COLORS['text_primary']
                            })
                        ])
                    ], style={'flex': '0 0 200px'}),

                    # Times
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-clock", style={
                                'marginRight': '6px',
                                'color': COLORS['text_secondary'],
                                'fontSize': '12px'
                            }),
                            html.Span(f"Departs: {origin_departure}", style={
                                'fontSize': '13px',
                                'color': COLORS['text_secondary'],
                                'display': 'block',
                                'marginBottom': '4px'
                            })
                        ], style={'marginBottom': '4px'}),
                        html.Div([
                            html.I(className="fas fa-clock", style={
                                'marginRight': '6px',
                                'color': COLORS['text_secondary'],
                                'fontSize': '12px'
                            }),
                            html.Span(f"Arrives: {destination_arrival}", style={
                                'fontSize': '13px',
                                'color': COLORS['text_secondary'],
                                'display': 'block'
                            })
                        ])
                    ], style={'flex': '0 0 150px'}),

                    # Status Toggle Button
                    html.Div([
                        dbc.Button([
                            html.I(className=f"fas fa-{status_style['icon']}", style={
                                'marginRight': '6px',
                                'fontSize': '12px'
                            }),
                            html.Span(status, style={
                                'fontWeight': '600',
                                'fontSize': '13px'
                            })
                        ], 
                        id={'type': 'toggle-schedule-status', 'index': schedule.get('train_schedule_id')},
                        style={
                            'background': status_style['bg'],
                            'color': status_style['color'],
                            'padding': '6px 14px',
                            'borderRadius': '8px',
                            'border': f'2px solid {status_style["color"]}40',
                            'cursor': 'pointer',
                            'transition': 'all 0.2s ease',
                            'fontWeight': '600',
                            'fontSize': '13px'
                        })
                    ], style={'flex': '0 0 120px', 'textAlign': 'center'}),

                ], style={
                    **row_style,
                    'display': 'flex',
                    'alignItems': 'center',
                    'gap': '20px',
                }, className='schedule-row')
            )

        # Create day info banner - simpler version since backend handles special days
        day_label = day_of_week.capitalize()

        # Summary header with day info
        summary = html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-calendar-day", style={
                        'marginRight': '8px',
                        'color': COLORS['primary'],
                        'fontSize': '14px'
                    }),
                    html.Span(f"{target_date.strftime('%B %d, %Y')} ({day_label})", style={
                        'fontSize': '14px',
                        'color': COLORS['text_primary'],
                        'fontWeight': '600',
                        'marginRight': '12px'
                    })
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'}),
                html.Div([
                    html.I(className="fas fa-info-circle", style={
                        'marginRight': '8px',
                        'color': COLORS['primary'],
                        'fontSize': '14px'
                    }),
                    html.Span(f"Showing {len(filtered_schedules)} schedule{'s' if len(filtered_schedules) != 1 else ''}", style={
                        'fontSize': '14px',
                        'color': COLORS['text_secondary'],
                        'fontWeight': '500'
                    })
                ], style={'display': 'flex', 'alignItems': 'center'})
            ])
        ], style={
            'padding': '16px 24px',
            'background': '#f8f9fa',
            'borderBottom': f'2px solid {COLORS["border"]}',
            'borderRadius': '12px 12px 0 0'
        })

        # Create count badge text
        count_text = f"{len(filtered_schedules)} Schedule{'s' if len(filtered_schedules) != 1 else ''}"

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
        }), count_text

    @callback(
        Output("filter-train-schedule-origin", "options"),
        [Input("url", "pathname"),
         Input("filter-train-schedule-origin", "search_value")],
        [State("filter-train-schedule-origin", "value")],
        prevent_initial_call=False
    )
    def load_origin_stations(pathname, search_value, current_value):
        """Load stations for origin filter dropdown with server-side search"""
        if pathname != "/schedules":
            return []
        
        try:
            # Use server-side search if user is typing
            if search_value and len(search_value) >= 2:
                stations = search_stations(search_value)
                logger.info(f"Origin search '{search_value}': got {len(stations) if stations else 0} stations")
            else:
                # Load initial 50 stations for fast load
                stations = get_stations_initial()
                logger.info(f"Origin initial load: got {len(stations) if stations else 0} stations")
            
            if not stations or not isinstance(stations, list):
                logger.warning(f"No valid stations data received for origin dropdown")
                return []
            
            opts = [{"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")} for s in stations]
            
            # If there's a current selection not in the new options, fetch and add it
            if current_value:
                existing_values = [opt["value"] for opt in opts]
                if current_value not in existing_values:
                    # Fetch the selected station to include it in options
                    selected_station = make_api_request(f"/stations/{current_value}", token=None, timeout=5)
                    if selected_station and isinstance(selected_station, dict):
                        opts.insert(0, {"label": selected_station.get("station_name", "Unknown"), "value": selected_station.get("station_id", "")})
                        logger.info(f"Added current selection {current_value} to origin options")
            
            return opts
        except Exception as e:
            logger.error(f"Error in load_origin_stations: {e}", exc_info=True)
            return []

    @callback(
        Output("filter-train-schedule-destination", "options"),
        [Input("url", "pathname"),
         Input("filter-train-schedule-origin", "value"),
         Input("filter-train-schedule-destination", "search_value")],
        [State("filter-train-schedule-destination", "value")],
        prevent_initial_call=False
    )
    def load_destination_stations(pathname, origin_value, search_value, current_value):
        """Load destination stations with server-side search, excluding the selected origin"""
        if pathname != "/schedules":
            return []
        
        try:
            # Use server-side search if user is typing
            if search_value and len(search_value) >= 2:
                stations = search_stations(search_value)
                logger.info(f"Destination search '{search_value}': got {len(stations) if stations else 0} stations")
            else:
                # Load initial 50 stations for fast load
                stations = get_stations_initial()
                logger.info(f"Destination initial load: got {len(stations) if stations else 0} stations")
            
            if not stations or not isinstance(stations, list):
                logger.warning(f"No valid stations data received for destination dropdown")
                return []
            
            # Filter out the origin station if selected
            if origin_value:
                stations = [s for s in stations if s.get("station_id") != origin_value]
                logger.info(f"Filtered out origin station {origin_value}, {len(stations)} stations remaining")
            
            opts = [{"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")} for s in stations]
            
            # If there's a current selection not in the new options, fetch and add it
            if current_value and current_value != origin_value:
                existing_values = [opt["value"] for opt in opts]
                if current_value not in existing_values:
                    # Fetch the selected station to include it in options
                    selected_station = make_api_request(f"/stations/{current_value}", token=None, timeout=5)
                    if selected_station and isinstance(selected_station, dict):
                        opts.insert(0, {"label": selected_station.get("station_name", "Unknown"), "value": selected_station.get("station_id", "")})
                        logger.info(f"Added current selection {current_value} to destination options")
            
            return opts
        except Exception as e:
            logger.error(f"Error in load_destination_stations: {e}", exc_info=True)
            return []

    @callback(
        [Output("filter-train-schedule-date", "value"),
         Output("filter-train-schedule-origin", "value"),
         Output("filter-train-schedule-destination", "value")],
        Input("clear-train-schedule-filters", "n_clicks"),
        prevent_initial_call=True
    )
    def clear_filters(n_clicks):
        """Clear all filters and reset to today's date"""
        return datetime.now().strftime("%Y-%m-%d"), None, None

    @callback(
        [Output("train-schedule-alert", "children"),
         Output("train-schedule-alert", "color"),
         Output("train-schedule-alert", "is_open"),
         Output("apply-train-schedule-filter", "n_clicks")],
        Input({'type': 'toggle-schedule-status', 'index': ALL}, 'n_clicks'),
        [State({'type': 'toggle-schedule-status', 'index': ALL}, 'id'),
         State("token-store", "data"),
         State("apply-train-schedule-filter", "n_clicks")],
        prevent_initial_call=True
    )
    def toggle_schedule_status(n_clicks_list, button_ids, token, current_apply_clicks):
        """Toggle train schedule status between Active and Inactive"""
        if not token or not any(n_clicks_list):
            return no_update, no_update, no_update, no_update
        
        # Find which button was clicked
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update
        
        triggered_id = ctx.triggered[0]['prop_id']
        
        # Extract schedule_id from triggered button
        import json
        try:
            button_id = json.loads(triggered_id.split('.')[0])
            schedule_id = button_id['index']
        except:
            return "Error: Could not identify schedule", "danger", True, no_update
        
        # Get current schedule to determine new status
        schedule = make_api_request(f"/schedules/{schedule_id}", token=token)
        if not schedule:
            return f"Schedule {schedule_id} not found", "danger", True, no_update
        
        current_status = schedule.get('status', 'Active')
        new_status = 'Inactive' if current_status == 'Active' else 'Active'
        
        # Update schedule status
        response = make_api_request(
            f"/schedules/{schedule_id}",
            method="PATCH",
            data={"status": new_status},
            token=token
        )
        
        if response:
            logger.info(f"Schedule {schedule_id} status updated to {new_status}")
            # Trigger table reload by incrementing apply filter clicks
            new_clicks = (current_apply_clicks or 0) + 1
            return f"Schedule {schedule_id} is now {new_status}", "success", True, new_clicks
        else:
            return f"Failed to update schedule {schedule_id}", "danger", True, no_update

    @callback(
        Output("add-schedule-modal", "is_open"),
        [Input("add-train-schedule-btn", "n_clicks"),
         Input("close-add-schedule-modal", "n_clicks"),
         Input("save-add-schedule-btn", "n_clicks")],
        State("add-schedule-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_add_schedule_modal(open_click, close_click, save_click, is_open):
        """Toggle add schedule modal visibility"""
        ctx = callback_context
        if not ctx.triggered:
            return is_open
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == "add-train-schedule-btn":
            return True
        elif button_id in ["close-add-schedule-modal", "save-add-schedule-btn"]:
            return False
        
        return is_open

    @callback(
        Output("add-schedule-id", "value"),
        Input("add-schedule-modal", "is_open"),
        State("token-store", "data"),
        prevent_initial_call=True
    )
    def auto_generate_schedule_id(is_open, token):
        """Auto-generate next schedule ID when modal opens"""
        if not is_open or not token:
            return ""
        
        next_id = generate_next_schedule_id(token)
        logger.info(f"Auto-generated schedule ID: {next_id}")
        return next_id

    @callback(
        Output("add-schedule-route", "options"),
        Input("add-schedule-modal", "is_open"),
        State("token-store", "data"),
        prevent_initial_call=True
    )
    def load_routes_for_add_schedule(is_open, token):
        """Load routes for add schedule modal"""
        if not is_open or not token:
            return []
        
        routes = make_api_request("/routes?limit=100", token=token)
        if routes and isinstance(routes, list):
            return [{"label": f"{r.get('route_id')} - {r.get('route_name', 'N/A')}", "value": r.get('route_id')} for r in routes]
        return []

    @callback(
        Output("add-schedule-origin-station", "options"),
        [Input("add-schedule-modal", "is_open"),
         Input("add-schedule-origin-station", "search_value")],
        [State("token-store", "data"),
         State("add-schedule-origin-station", "value")],
        prevent_initial_call=True
    )
    def load_origin_for_add_schedule(is_open, search_value, token, current_value):
        """Load origin stations for add schedule modal"""
        if not is_open:
            return []
        
        if search_value and len(search_value) >= 2:
            stations = search_stations(search_value)
        else:
            stations = get_stations_initial()
        
        if not stations:
            return []
        
        opts = [{"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")} for s in stations]
        
        if current_value:
            existing_values = [opt["value"] for opt in opts]
            if current_value not in existing_values:
                selected_station = make_api_request(f"/stations/{current_value}", token=None, timeout=5)
                if selected_station:
                    opts.insert(0, {"label": selected_station.get("station_name", "Unknown"), "value": selected_station.get("station_id", "")})
        
        return opts

    @callback(
        Output("add-schedule-destination-station", "options"),
        [Input("add-schedule-modal", "is_open"),
         Input("add-schedule-origin-station", "value"),
         Input("add-schedule-destination-station", "search_value")],
        [State("token-store", "data"),
         State("add-schedule-destination-station", "value")],
        prevent_initial_call=True
    )
    def load_destination_for_add_schedule(is_open, origin_value, search_value, token, current_value):
        """Load destination stations for add schedule modal, excluding origin"""
        if not is_open:
            return []
        
        if search_value and len(search_value) >= 2:
            stations = search_stations(search_value)
        else:
            stations = get_stations_initial()
        
        if not stations:
            return []
        
        # Filter out origin station
        if origin_value:
            stations = [s for s in stations if s.get("station_id") != origin_value]
        
        opts = [{"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")} for s in stations]
        
        if current_value and current_value != origin_value:
            existing_values = [opt["value"] for opt in opts]
            if current_value not in existing_values:
                selected_station = make_api_request(f"/stations/{current_value}", token=None, timeout=5)
                if selected_station:
                    opts.insert(0, {"label": selected_station.get("station_name", "Unknown"), "value": selected_station.get("station_id", "")})
        
        return opts

    @callback(
        Output("add-schedule-name", "value"),
        [Input("add-schedule-origin-station", "value"),
         Input("add-schedule-destination-station", "value")],
        State("token-store", "data"),
        prevent_initial_call=True
    )
    def auto_generate_schedule_name(origin_id, destination_id, token):
        """Auto-generate schedule name from origin and destination stations"""
        if not origin_id or not destination_id:
            return ""
        
        try:
            # Fetch station names
            origin_station = make_api_request(f"/stations/{origin_id}", token=None, timeout=5)
            destination_station = make_api_request(f"/stations/{destination_id}", token=None, timeout=5)
            
            if origin_station and destination_station:
                origin_name = origin_station.get("station_name", "Unknown")
                destination_name = destination_station.get("station_name", "Unknown")
                schedule_name = f"{origin_name} To {destination_name}"
                logger.info(f"Auto-generated schedule name: {schedule_name}")
                return schedule_name
        except Exception as e:
            logger.error(f"Error generating schedule name: {e}")
        
        return ""

    @callback(
        [Output("add-schedule-modal-alert", "children"),
         Output("add-schedule-modal-alert", "color"),
         Output("add-schedule-modal-alert", "is_open"),
         Output("train-schedule-alert", "children", allow_duplicate=True),
         Output("train-schedule-alert", "color", allow_duplicate=True),
         Output("train-schedule-alert", "is_open", allow_duplicate=True),
         Output("apply-train-schedule-filter", "n_clicks", allow_duplicate=True)],
        Input("save-add-schedule-btn", "n_clicks"),
        [State("add-schedule-id", "value"),
         State("add-schedule-route", "value"),
         State("add-schedule-name", "value"),
         State("add-schedule-origin-station", "value"),
         State("add-schedule-origin-time", "value"),
         State("add-schedule-destination-station", "value"),
         State("add-schedule-destination-time", "value"),
         State("add-schedule-weekdays", "value"),
         State("add-schedule-special-days", "value"),
         State("add-schedule-status", "value"),
         State("token-store", "data"),
         State("apply-train-schedule-filter", "n_clicks")],
        prevent_initial_call=True
    )
    def save_new_schedule(n_clicks, schedule_id, route_id, schedule_name, origin_station_id, origin_time,
                         destination_station_id, destination_time, weekdays, special_days, status, token, current_apply_clicks):
        """Save new train schedule"""
        if not n_clicks or not token:
            return "", "info", False, "", "info", False, no_update
        
        # Validation
        if not all([schedule_id, route_id, schedule_name, origin_station_id, origin_time, 
                   destination_station_id, destination_time]):
            return "Please fill in all required fields", "warning", True, "", "info", False, no_update
        
        if not weekdays and not special_days:
            return "Please select at least one operating day", "warning", True, "", "info", False, no_update
        
        # Get station names
        origin_station = make_api_request(f"/stations/{origin_station_id}", token=token)
        destination_station = make_api_request(f"/stations/{destination_station_id}", token=token)
        
        if not origin_station or not destination_station:
            return "Invalid station selection", "danger", True, "", "info", False, no_update
        
        # Build schedule data
        schedule_data = {
            "train_schedule_id": schedule_id,
            "route_id": route_id,
            "train_schedule": schedule_name,
            "origin_station_id": origin_station_id,
            "origin_station": origin_station.get("station_name"),
            "origin_departure": origin_time,
            "destination_station_id": destination_station_id,
            "destination_station": destination_station.get("station_name"),
            "destination_departure": destination_time,
            "monday": "monday" in weekdays,
            "tuesday": "tuesday" in weekdays,
            "wednesday": "wednesday" in weekdays,
            "thursday": "thursday" in weekdays,
            "friday": "friday" in weekdays,
            "saturday": "saturday" in weekdays,
            "sunday": "sunday" in weekdays,
            "poya_day": "poya_day" in special_days if special_days else False,
            "holiday": "holiday" in special_days if special_days else False,
            "status": status
        }
        
        # Send to backend
        response = make_api_request(
            "/schedules",
            method="POST",
            data=schedule_data,
            token=token
        )
        
        if response:
            logger.info(f"Schedule {schedule_id} created successfully")
            # Trigger table reload
            new_clicks = (current_apply_clicks or 0) + 1
            return "", "info", False, f"Schedule {schedule_id} created successfully!", "success", True, new_clicks
        else:
            return "Failed to create schedule. Please check if Schedule ID already exists.", "danger", True, "", "info", False, no_update
