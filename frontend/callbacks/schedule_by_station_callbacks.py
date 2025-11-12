"""
TCDAFS - Schedule by Station Callbacks
Handle schedule search by origin/destination stations
"""
from dash import callback, Input, Output, State, html, no_update, ALL, ctx
import dash_bootstrap_components as dbc
from utils.api import make_api_request
from utils.cache import get_cached
from config.styles import COLORS
import logging

logger = logging.getLogger(__name__)


def search_stations(search_query, token):
    """Search stations by name with server-side filtering"""
    if not search_query or len(search_query) < 2:
        # If no search or too short, return initial list
        stations = make_api_request("/stations?limit=50", token=token, timeout=10)
        return stations if (stations and isinstance(stations, list)) else []
    
    # Search on backend with query - only returns matching stations
    stations = make_api_request(f"/stations?search={search_query}&limit=50", token=token, timeout=10)
    logger.info(f"Searched stations with query '{search_query}', found {len(stations) if stations else 0} results")
    return stations if (stations and isinstance(stations, list)) else []


def register(app):
    """Register schedule by station callbacks with the app"""

    @callback(
        Output("schedule-origin-station", "options"),
        [Input("url", "pathname"),
         Input("token-store", "data"),
         Input("schedule-origin-station", "search_value")],
        State("schedule-origin-station", "value"),
        prevent_initial_call=False
    )
    def load_schedule_origin_stations(pathname, token, search_value, current_value):
        """Load origin stations for schedule search with server-side search"""
        if pathname != "/schedule-stations" or not token:
            return []

        try:
            # Use server-side search if user is typing
            if search_value and len(search_value) >= 2:
                stations = search_stations(search_value, token)
            else:
                # Load initial 50 stations
                stations = make_api_request("/stations?limit=50", token=token, timeout=10)
            
            if stations and isinstance(stations, list):
                opts = [{"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")} for s in stations]
                return opts
        except Exception as e:
            logger.error(f"Error loading origin stations: {e}")
        return []

    @callback(
        Output("schedule-destination-station", "options"),
        [Input("url", "pathname"),
         Input("token-store", "data"),
         Input("schedule-destination-station", "search_value")],
        State("schedule-destination-station", "value"),
        prevent_initial_call=False
    )
    def load_schedule_destination_stations(pathname, token, search_value, current_value):
        """Load destination stations for schedule search with server-side search"""
        if pathname != "/schedule-stations" or not token:
            return []

        try:
            # Use server-side search if user is typing
            if search_value and len(search_value) >= 2:
                stations = search_stations(search_value, token)
            else:
                # Load initial 50 stations
                stations = make_api_request("/stations?limit=50", token=token, timeout=10)
            
            if stations and isinstance(stations, list):
                opts = [{"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")} for s in stations]
                return opts
        except Exception as e:
            logger.error(f"Error loading destination stations: {e}")
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
    def search_schedules(n_clicks, origin, destination, date, token):
        """Search schedules by origin/destination/date using train_schedule_by_station table"""
        if not n_clicks or not token:
            return html.Div(), "", False, "info"

        if not origin:
            return html.Div(), "Please select an origin station", True, "warning"

        # Build query parameters for train_schedule_by_station with day filtering
        params = f"origin_station_id={origin}"
        if destination:
            params += f"&destination_station_id={destination}"
        if date:
            params += f"&travel_date={date}"
        
        # Query the train_schedule_by_station table with JOIN to train_schedules
        endpoint = f"/schedule-by-station?{params}&limit=500"
        schedules = make_api_request(endpoint, token=token, timeout=10)

        if not schedules or not isinstance(schedules, list) or len(schedules) == 0:
            return (
                html.Div([
                    dbc.Alert([
                        html.I(className="fas fa-info-circle", style={'marginRight': '8px', 'fontSize': '20px'}),
                        html.P("No schedules found for the selected criteria", style={'margin': '0'})
                    ], color="info")
                ], style={'marginTop': '24px'}),
                "No schedules found", True, "info"
            )

        # Display results in a table format
        table_rows = []
        for idx, s in enumerate(schedules):
            segment_id = s.get('id', 'N/A')
            train_schedule_id = s.get('train_schedule_id', 'N/A')
            train_schedule = s.get('train_schedule', 'N/A')
            origin_station = s.get('origin_station', 'N/A')
            origin_departure = s.get('origin_departure', 'N/A')
            destination_station = s.get('destination_station', 'N/A')
            destination_arrival = s.get('destination_departure', 'N/A')
            duration = s.get('duration', 'N/A')
            
            # Store original times for edit
            original_origin_time = origin_departure
            original_dest_time = destination_arrival
            
            # Format time if needed
            if origin_departure and origin_departure != 'N/A':
                try:
                    if len(str(origin_departure)) > 5:
                        origin_departure = str(origin_departure)[:5]
                except:
                    pass
            
            if destination_arrival and destination_arrival != 'N/A':
                try:
                    if len(str(destination_arrival)) > 5:
                        destination_arrival = str(destination_arrival)[:5]
                except:
                    pass

            row_style = {
                'borderBottom': f'1px solid {COLORS["border"]}',
                'padding': '16px 20px',
                'background': '#ffffff' if idx % 2 == 0 else '#fafbfc',
                'transition': 'all 0.2s ease'
            }

            table_rows.append(
                html.Div([
                    # Schedule ID
                    html.Div([
                        html.Span(train_schedule_id, style={
                            'background': f'{COLORS["primary"]}15',
                            'color': COLORS['primary'],
                            'padding': '6px 12px',
                            'borderRadius': '6px',
                            'fontWeight': '600',
                            'fontSize': '12px',
                            'border': f'1px solid {COLORS["primary"]}30'
                        })
                    ], style={'flex': '0 0 120px'}),

                    # Train Name
                    html.Div([
                        html.I(className="fas fa-train", style={
                            'marginRight': '8px',
                            'color': COLORS['primary'],
                            'fontSize': '13px'
                        }),
                        html.Span(train_schedule, style={
                            'fontWeight': '600',
                            'fontSize': '14px',
                            'color': COLORS['text_primary']
                        })
                    ], style={'flex': '1', 'minWidth': '0'}),

                    # Origin
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-map-marker-alt", style={
                                'marginRight': '6px',
                                'color': '#059669',
                                'fontSize': '12px'
                            }),
                            html.Span(origin_station, style={
                                'fontSize': '13px',
                                'fontWeight': '500'
                            })
                        ], style={'marginBottom': '4px'}),
                        html.Div([
                            html.I(className="fas fa-clock", style={
                                'marginRight': '6px',
                                'color': COLORS['text_secondary'],
                                'fontSize': '11px'
                            }),
                            html.Span(origin_departure, style={
                                'fontSize': '12px',
                                'color': COLORS['text_secondary']
                            })
                        ])
                    ], style={'flex': '0 0 180px'}),

                    # Arrow
                    html.Div([
                        html.I(className="fas fa-arrow-right", style={
                            'color': COLORS['text_secondary'],
                            'fontSize': '16px'
                        })
                    ], style={'flex': '0 0 40px', 'textAlign': 'center'}),

                    # Destination
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-map-marker-alt", style={
                                'marginRight': '6px',
                                'color': '#dc2626',
                                'fontSize': '12px'
                            }),
                            html.Span(destination_station, style={
                                'fontSize': '13px',
                                'fontWeight': '500'
                            })
                        ], style={'marginBottom': '4px'}),
                        html.Div([
                            html.I(className="fas fa-clock", style={
                                'marginRight': '6px',
                                'color': COLORS['text_secondary'],
                                'fontSize': '11px'
                            }),
                            html.Span(destination_arrival, style={
                                'fontSize': '12px',
                                'color': COLORS['text_secondary']
                            })
                        ])
                    ], style={'flex': '0 0 180px'}),

                    # Duration
                    html.Div([
                        html.I(className="fas fa-hourglass-half", style={
                            'marginRight': '6px',
                            'color': COLORS['info'],
                            'fontSize': '12px'
                        }),
                        html.Span(str(duration), style={
                            'fontSize': '13px',
                            'fontWeight': '500',
                            'color': COLORS['info']
                        })
                    ], style={'flex': '0 0 120px', 'textAlign': 'center'}),

                    # Edit Button
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-edit", style={'marginRight': '6px'}),
                            "Edit Times"
                        ], id={'type': 'edit-segment-btn', 'index': segment_id}, 
                        color="primary", size="sm", outline=True, style={
                            'fontSize': '12px',
                            'padding': '6px 12px'
                        })
                    ], style={'flex': '0 0 120px', 'textAlign': 'right'})

                ], style={
                    **row_style,
                    'display': 'flex',
                    'alignItems': 'center',
                    'gap': '16px',
                }, className='schedule-row')
            )

        return (
            html.Div([
                html.Div([
                    html.H5([
                        html.I(className="fas fa-list", style={'marginRight': '10px', 'color': COLORS['primary']}),
                        f"Found {len(schedules)} Schedule Segment(s)"
                    ], style={'marginBottom': '20px', 'color': COLORS['text_primary'], 'fontWeight': '700'})
                ]),
                html.Div([
                    html.Div(table_rows, style={
                        'background': '#ffffff',
                        'borderRadius': '12px',
                        'overflow': 'hidden',
                        'boxShadow': '0 2px 8px rgba(0,0,0,0.05)'
                    })
                ])
            ]),
            f"Found {len(schedules)} schedule segment(s)", True, "success"
        )

    @callback(
        [Output("edit-time-modal", "is_open"),
         Output("edit-origin-departure", "value"),
         Output("edit-destination-arrival", "value"),
         Output("edit-segment-id", "children"),
         Output("edit-time-schedule-info", "children"),
         Output("edit-time-alert", "children"),
         Output("edit-time-alert", "is_open"),
         Output("edit-time-alert", "color")],
        [Input({'type': 'edit-segment-btn', 'index': ALL}, 'n_clicks'),
         Input("close-edit-time-modal", "n_clicks"),
         Input("save-edit-time-btn", "n_clicks")],
        [State("edit-segment-id", "children"),
         State("edit-origin-departure", "value"),
         State("edit-destination-arrival", "value"),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def handle_edit_time_modal(edit_clicks, close_clicks, save_clicks, 
                               segment_id, origin_time, dest_time, token):
        """Handle opening and closing edit time modal"""
        if not ctx.triggered:
            return False, "", "", "", html.Div(), "", False, "info"
        
        triggered_id = ctx.triggered[0]['prop_id']
        
        # Check if any edit button was actually clicked (not just created)
        if "edit-segment-btn" in triggered_id:
            # Check if any button was actually clicked (n_clicks > 0)
            if not any(edit_clicks) or all(click is None for click in edit_clicks):
                return False, "", "", "", html.Div(), "", False, "info"
        
        # Close button clicked
        if "close-edit-time-modal" in triggered_id:
            return False, "", "", "", html.Div(), "", False, "info"
        
        # Save button clicked
        if "save-edit-time-btn" in triggered_id and segment_id:
            if not origin_time or not dest_time:
                return True, origin_time, dest_time, segment_id, no_update, "Please fill in both times", True, "warning"
            
            # Update the schedule segment via API
            update_data = {
                "origin_departure": origin_time,
                "destination_departure": dest_time
            }
            
            result = make_api_request(
                f"/schedule-by-station/{segment_id}",
                method="PUT",
                data=update_data,
                token=token
            )
            
            if result:
                # Close modal and show success
                return False, "", "", "", html.Div(), "Times updated successfully!", True, "success"
            else:
                return True, origin_time, dest_time, segment_id, no_update, "Failed to update times. Please try again.", True, "danger"
        
        # Edit button clicked - find which one
        if "edit-segment-btn" in triggered_id:
            # Get the segment ID from the triggered button
            import json
            button_id = json.loads(triggered_id.split('.')[0])
            seg_id = button_id['index']
            
            # Fetch segment details
            segment = make_api_request(f"/schedule-by-station/{seg_id}", token=token)
            
            if segment:
                origin_dep = segment.get('origin_departure', '')
                dest_arr = segment.get('destination_departure', '')
                
                # Format times to HH:MM for time input
                if origin_dep and len(str(origin_dep)) > 5:
                    origin_dep = str(origin_dep)[:5]
                if dest_arr and len(str(dest_arr)) > 5:
                    dest_arr = str(dest_arr)[:5]
                
                # Create info display
                info_div = html.Div([
                    html.H6([
                        html.I(className="fas fa-train", style={'marginRight': '8px', 'color': COLORS['primary']}),
                        segment.get('train_schedule', 'N/A')
                    ], style={'color': COLORS['text_primary'], 'marginBottom': '8px'}),
                    html.P([
                        html.I(className="fas fa-map-marker-alt", style={'marginRight': '6px', 'color': '#059669'}),
                        f"{segment.get('origin_station', 'N/A')} → ",
                        html.I(className="fas fa-map-marker-alt", style={'marginRight': '6px', 'marginLeft': '12px', 'color': '#dc2626'}),
                        segment.get('destination_station', 'N/A')
                    ], style={'color': COLORS['text_secondary'], 'fontSize': '14px', 'margin': '0'})
                ], style={
                    'padding': '12px',
                    'background': '#f8f9fa',
                    'borderRadius': '8px',
                    'border': f'1px solid {COLORS["border"]}'
                })
                
                return True, origin_dep, dest_arr, str(seg_id), info_div, "", False, "info"
        
        return False, "", "", "", html.Div(), "", False, "info"

