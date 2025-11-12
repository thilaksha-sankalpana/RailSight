"""
TCDAFS - Ticket Booking Callbacks
Handle ticket booking, schedule search, price calculation, and ticket cancellation
"""
from dash import callback, Input, Output, State, html, no_update, dash, ALL, MATCH, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from utils.api import make_api_request
from utils.cache import get_cached
from config.styles import COLORS
import logging

logger = logging.getLogger(__name__)


def get_stations_initial():
    """Get initial list of stations (top 50) for quick loading"""
    def fetch_stations():
        stations = make_api_request("/stations?limit=50", token=None, timeout=15)
        return stations if (stations and isinstance(stations, list)) else []

    return get_cached("stations_initial", fetch_stations, ttl_minutes=10)


def search_stations(search_query):
    """Search stations by name with server-side filtering"""
    if not search_query or len(search_query) < 2:
        return get_stations_initial()

    stations = make_api_request(f"/stations?search={search_query}&limit=20", token=None, timeout=10)
    return stations if (stations and isinstance(stations, list)) else []


def register(app):
    """Register ticket booking callbacks with the app"""

    @callback(
        Output("ticket-origin", "options"),
        [Input("url", "pathname"),
         Input("ticket-origin", "search_value")],
        [State("token-store", "data"),
         State("ticket-origin", "value")],
        prevent_initial_call=False
    )
    def load_origin_stations(pathname, search_value, token, current_value):
        """Load stations for origin dropdown with server-side search"""
        if pathname != "/tickets":
            return []

        try:
            if search_value and len(search_value) >= 2:
                stations = search_stations(search_value)
            else:
                stations = get_stations_initial()

            if not stations or not isinstance(stations, list):
                return []

            opts = [{"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")} for s in stations]

            # If there's a current selection not in the new options, fetch and add it
            if current_value:
                existing_values = [opt["value"] for opt in opts]
                if current_value not in existing_values:
                    selected_station = make_api_request(f"/stations/{current_value}", token=None, timeout=5)
                    if selected_station and isinstance(selected_station, dict):
                        opts.insert(0, {"label": selected_station.get("station_name", "Unknown"), "value": selected_station.get("station_id", "")})

            return opts
        except Exception as e:
            logger.error(f"Error in load_origin_stations: {e}", exc_info=True)
            return []

    @callback(
        Output("ticket-destination", "options"),
        [Input("url", "pathname"),
         Input("ticket-origin", "value"),
         Input("ticket-destination", "search_value")],
        [State("token-store", "data"),
         State("ticket-destination", "value")],
        prevent_initial_call=False
    )
    def load_destination_stations(pathname, origin_value, search_value, token, current_value):
        """Load destination stations with server-side search, excluding the selected origin"""
        if pathname != "/tickets":
            return []

        try:
            if search_value and len(search_value) >= 2:
                stations = search_stations(search_value)
            else:
                stations = get_stations_initial()

            if not stations or not isinstance(stations, list):
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
                        opts.insert(0, {"label": selected_station.get("station_name", "Unknown"), "value": selected_station.get("station_id", "")})

            return opts
        except Exception as e:
            logger.error(f"Error in load_destination_stations: {e}", exc_info=True)
            return []

    @callback(
        Output("available-schedules", "children"),
        Input("search-trains-btn", "n_clicks"),
        [State("ticket-origin", "value"),
         State("ticket-destination", "value"),
         State("ticket-date", "value"),
         State("ticket-time", "value"),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def load_schedules_display(n_clicks, origin, dest, date, travel_time, token):
        """Display available train schedules for selected route and date - only when search button is clicked"""
        if not n_clicks:
            return html.Div()
            
        if not all([origin, dest, date, token]):
            return dbc.Alert([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                "Please select origin station, destination station, and travel date before searching."
            ], color="warning", style={'padding': '16px'})

        # Use the correct API endpoint - /schedules/available with travel_date parameter
        endpoint = f"/schedules/available?origin_station_id={origin}&destination_station_id={dest}&travel_date={date}"
        schedules = make_api_request(endpoint, token=token, timeout=10000)

        # Filter schedules based on travel time if provided
        if travel_time and schedules and isinstance(schedules, list):
            filtered_schedules = []
            for s in schedules:
                origin_departure = s.get('origin_departure', '')
                if origin_departure:
                    try:
                        # Extract just HH:MM for comparison
                        departure_time = origin_departure.split(':')[:2]
                        departure_time_str = ':'.join(departure_time)
                        
                        if departure_time_str >= travel_time:
                            filtered_schedules.append(s)
                    except Exception:
                        # Include schedule if time parsing fails
                        filtered_schedules.append(s)
            
            schedules = filtered_schedules

        if not schedules or not isinstance(schedules, list) or len(schedules) == 0:

            # Get day of week for better error message
            from datetime import datetime as dt
            try:
                date_obj = dt.strptime(date, "%Y-%m-%d")
                day_name = date_obj.strftime("%A")
            except:
                day_name = "selected day"

            time_message = f" departing after {travel_time}" if travel_time else ""

            return dbc.Alert([
                html.I(className="fas fa-info-circle", style={'marginRight': '8px', 'fontSize': '20px'}),
                html.Div([
                    html.Strong(f"No trains found for this route{time_message}", style={'display': 'block', 'marginBottom': '8px'}),
                    html.P(f"Travel date: {date} ({day_name})", style={'margin': '4px 0', 'fontSize': '13px'}),
                    html.P("Possible reasons:", style={'fontWeight': '600', 'marginTop': '12px', 'marginBottom': '6px'}),
                    html.Ul([
                        html.Li(f"No trains operate on this route on {day_name}s"),
                        html.Li("All trains depart before your selected time") if travel_time else None,
                        html.Li("The stations are not on the same train route"),
                        html.Li("Schedules for this route are inactive"),
                        html.Li("Try selecting a different date, time, or route")
                    ], style={'marginTop': '8px', 'marginBottom': '8px', 'fontSize': '13px'}),
                    html.Hr(style={'margin': '12px 0'}),
                    html.P([
                        html.I(className="fas fa-lightbulb", style={'marginRight': '6px', 'color': COLORS['warning']}),
                        html.Strong("Tip: "),
                        "Check the 'Schedule by Station' tab to see all trains operating from your origin station."
                    ], style={'fontSize': '12px', 'color': COLORS['text_secondary']})
                ])
            ], color="warning", style={'padding': '20px'})

        schedule_cards = []
        for s in schedules:
            train_name = s.get('train_schedule', 'N/A')
            origin_departure = s.get('origin_departure', 'N/A')
            destination_arrival = s.get('destination_departure', 'N/A')

            # Parse duration
            duration_str = s.get('duration', '')
            if duration_str and isinstance(duration_str, str):
                try:
                    parts = duration_str.split(':')
                    hours = int(parts[0]) if len(parts) > 0 else 0
                    mins = int(parts[1]) if len(parts) > 1 else 0
                    duration_text = f"{hours}h {mins}m" if hours > 0 else f"{mins} minutes"
                except (ValueError, IndexError):
                    duration_text = duration_str
            else:
                duration_text = "Duration not available"

            # Get available classes
            available_classes_data = s.get('available_classes', [])
            
            if isinstance(available_classes_data, list) and len(available_classes_data) > 0:
                if isinstance(available_classes_data[0], dict):
                    available_classes = [cls_info.get('class') for cls_info in available_classes_data if cls_info.get('class')]
                else:
                    available_classes = available_classes_data
            elif isinstance(available_classes_data, str):
                available_classes = [c.strip() for c in available_classes_data.split(',') if c.strip()]
            else:
                available_classes = ['First', 'Second', 'Third']

            # Create class badges
            class_badges = []
            class_colors_map = {'First': COLORS['primary'], 'Second': COLORS['info'], 'Third': COLORS['success']}
            for cls in available_classes:
                class_badges.append(
                    html.Span(cls, style={
                        'padding': '2px 8px',
                        'background': class_colors_map.get(cls, COLORS['text_secondary']),
                        'color': 'white',
                        'borderRadius': '4px',
                        'fontSize': '10px',
                        'fontWeight': '600',
                        'marginLeft': '4px'
                    })
                )

            schedule_cards.append(
                html.Div([
                    dbc.RadioItems(
                        id={"type": "schedule-radio", "index": s["train_schedule_id"]},
                        options=[{
                            "label": html.Div([
                                html.Div([
                                    html.I(className="fas fa-train", style={'marginRight': '12px', 'color': COLORS['primary'], 'fontSize': '24px'}),
                                    html.Div([
                                        html.Div([
                                            html.Strong(train_name, style={'fontSize': '16px', 'marginRight': '8px'}),
                                            *class_badges
                                        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '4px'}),
                                        html.Div([
                                            html.I(className="fas fa-clock", style={'marginRight': '6px', 'fontSize': '11px'}),
                                            html.Span(f"Departs: {origin_departure}", style={'marginRight': '12px', 'fontSize': '13px'}),
                                            html.I(className="fas fa-flag-checkered", style={'marginRight': '6px', 'fontSize': '11px'}),
                                            html.Span(f"Arrives: {destination_arrival}", style={'fontSize': '13px'})
                                        ], style={'color': COLORS['text_secondary'], 'marginBottom': '2px'}),
                                        html.Div([
                                            html.I(className="fas fa-hourglass-half", style={'marginRight': '6px', 'fontSize': '11px'}),
                                            html.Span(f"Duration: {duration_text}", style={'fontSize': '12px', 'color': COLORS['info'], 'fontWeight': '500'})
                                        ])
                                    ], style={'flex': '1'})
                                ], style={'display': 'flex', 'alignItems': 'center', 'width': '100%'})
                            ]),
                            "value": s["train_schedule_id"]
                        }],
                        value=None
                    ),
                    # Hidden div to store available classes for this schedule
                    html.Div(
                        ','.join(available_classes) if available_classes else '',
                        id={"type": "schedule-classes", "index": s["train_schedule_id"]},
                        style={'display': 'none'}
                    ),
                    # Hidden store for full schedule data
                    dcc.Store(
                        id={"type": "schedule-data", "index": s["train_schedule_id"]},
                        data=s
                    )
                ], style={
                    'padding': '16px',
                    'background': '#f8fafc',
                    'borderRadius': '8px',
                    'marginBottom': '12px',
                    'border': f'2px solid {COLORS["border"]}',
                    'cursor': 'pointer',
                    'transition': 'all 0.3s ease'
                }, className="schedule-option")
            )

        return html.Div([
            html.Label("Available Train Schedules *", style={'fontWeight': '600', 'marginBottom': '12px'}),
            html.P("Click on a schedule to select it for booking", style={
                'fontSize': '12px',
                'color': COLORS['text_secondary'],
                'marginBottom': '8px'
            }),
            html.Div(schedule_cards)
        ])

    @callback(
        [Output("selected-schedule-store", "data"),
         Output("ticket-class", "options"),
         Output("ticket-class", "value")],
        [Input({"type": "schedule-radio", "index": ALL}, "value")],
        [State({"type": "schedule-data", "index": ALL}, "data"),
         State({"type": "schedule-classes", "index": ALL}, "children")],
        prevent_initial_call=True
    )
    def store_selected_schedule_and_update_classes(selected_values, schedule_data_list, available_classes_list):
        """Store the selected train schedule and update available class options"""
        if not selected_values:
            return None, [], None

        # Find the first non-None value (selected schedule) and its index
        selected_schedule_id = None
        selected_index = None
        for idx, val in enumerate(selected_values):
            if val is not None:
                selected_schedule_id = val
                selected_index = idx
                break

        if selected_schedule_id is None:
            return None, [], None

        # Get the full schedule data
        schedule_data = None
        if selected_index is not None and selected_index < len(schedule_data_list):
            schedule_data = schedule_data_list[selected_index]

        # Get the available classes for the selected schedule
        available_classes_str = available_classes_list[selected_index] if selected_index < len(available_classes_list) else ""
        available_classes = [c.strip() for c in available_classes_str.split(',') if c.strip()] if available_classes_str else []

        # Create class options based on what's available
        class_options = []
        class_labels = {"First": "1st Class", "Second": "2nd Class", "Third": "3rd Class"}

        if available_classes:
            for cls in available_classes:
                class_options.append({"label": class_labels.get(cls, cls), "value": cls})
        else:
            # Fallback to all classes if none specified
            class_options = [
                {"label": "1st Class", "value": "First"},
                {"label": "2nd Class", "value": "Second"},
                {"label": "3rd Class", "value": "Third"}
            ]

        # Set default value to the first available class
        default_value = class_options[0]["value"] if class_options else None

        return schedule_data, class_options, default_value

    @callback(
        Output("ticket-price", "children"),
        [Input("ticket-origin", "value"),
         Input("ticket-destination", "value"),
         Input("ticket-class", "value"),
         Input("ticket-count-store", "data"),
         Input({"type": "passenger-type", "index": ALL}, "value")],
        prevent_initial_call=True
    )
    def update_ticket_price(origin, destination, train_class, ticket_count, passenger_types):
        """Calculate and display total ticket price"""
        if not all([origin, destination, train_class, ticket_count]):
            return "LKR 0.00"

        try:
            total_price = 0
            
            if not passenger_types or len(passenger_types) == 0:
                passenger_types = ["adult"] * ticket_count

            for i in range(ticket_count):
                is_child = (passenger_types[i] == "child") if i < len(passenger_types) else False

                payload = {
                    "origin_station_id": origin,
                    "destination_station_id": destination,
                    "class_": train_class,
                    "passengers": 1,
                    "is_child": is_child
                }

                response = make_api_request("/tickets/calculate-price", method="POST", data=payload)

                if response and "total" in response:
                    total_price += float(response["total"])

            return f"LKR {total_price:,.2f}"

        except Exception:
            return "LKR 0.00"

    @callback(
        [Output("ticket-alert", "children"),
         Output("ticket-alert", "is_open"),
         Output("ticket-alert", "color"),
         Output("booked-tickets-store", "data"),
         Output("ticket-print-modal", "is_open")],
        Input("book-ticket-btn", "n_clicks"),
        [State("ticket-origin", "value"),
         State("ticket-destination", "value"),
         State("selected-schedule-store", "data"),
         State("ticket-class", "value"),
         State("ticket-date", "value"),
         State("ticket-count-store", "data"),
         State({"type": "passenger-nic", "index": ALL}, "value"),
         State({"type": "passenger-contact", "index": ALL}, "value"),
         State({"type": "passenger-type", "index": ALL}, "value"),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def book_ticket(n, origin, dest, sched, cls, date, ticket_count, nic_list, contact_list, type_list, token):
        """Book tickets for all passengers"""
        if not n or not token:
            return "", False, "danger", None, False

        if not all([origin, dest, cls, date]):
            return "Please fill all required fields (origin, destination, class, date)", True, "warning", None, False

        if not sched or not isinstance(sched, dict):
            return "Please select a train schedule", True, "warning", None, False

        if not ticket_count or ticket_count < 1:
            return "Please select at least one ticket", True, "warning", None, False

        schedule_id = sched.get("train_schedule_id")
        origin_departure = sched.get("origin_departure", "00:00")
        destination_arrival = sched.get("destination_departure", "00:00")

        if not schedule_id:
            return "Invalid schedule selected", True, "danger", None, False

        booked_tickets = []
        booked_tickets_details = []  # Store full ticket details
        failed_bookings = 0

        for i in range(ticket_count):
            passenger_nic = nic_list[i] if i < len(nic_list) else None
            passenger_contact = contact_list[i] if i < len(contact_list) else None
            passenger_type = type_list[i] if i < len(type_list) else "adult"
            is_child = (passenger_type == "child")

            # NIC/Passport is required for both adults and children
            if not passenger_nic:
                passenger_label = "Child" if is_child else "Adult"
                return f"Please enter NIC/Passport for Passenger {i+1} ({passenger_label})", True, "warning", None, False

            # Contact number is optional for both adults and children
            passenger_contact = passenger_contact or None

            price_request = {
                "origin_station_id": origin,
                "destination_station_id": dest,
                "class_": cls,
                "passengers": 1,
                "is_child": is_child
            }

            price_response = make_api_request("/tickets/calculate-price", method="POST", data=price_request)

            if not price_response or "total" not in price_response:
                return f"Failed to calculate price for Passenger {i+1}", True, "danger", None, False

            ticket_fee = float(price_response["total"])

            ticket_data = {
                "schedule_date": date,
                "schedule_id": schedule_id,
                "origin_station_id": origin,
                "destination_station_id": dest,
                "origin_departure": origin_departure,
                "destination_departure": destination_arrival,
                "class_": cls,
                "fee": ticket_fee,
                "contact_number": passenger_contact,
                "payment_method": "Cash",
                "booking_platform": "Website",
                "is_child": is_child,
                "issue_date": date
            }

            if passenger_nic and not passenger_nic.startswith("CHILD-"):
                if any(c.isalpha() for c in passenger_nic.replace('V', '').replace('X', '')):
                    ticket_data["passport"] = passenger_nic
                else:
                    ticket_data["nic"] = passenger_nic
            else:
                ticket_data["passport"] = passenger_nic

            # Use longer timeout for ticket booking (15 seconds) due to capacity checks
            result = make_api_request("/tickets", method="POST", token=token, data=ticket_data, timeout=15)

            if result and "ticket_id" in result:
                booked_tickets.append(result['ticket_id'])
                # Fetch complete ticket details from API
                ticket_details = make_api_request(f"/tickets/{result['ticket_id']}", token=token)
                if ticket_details:
                    ticket_details['passenger_nic'] = passenger_nic
                    ticket_details['passenger_type'] = passenger_type
                    booked_tickets_details.append(ticket_details)
                else:
                    # Fallback to result if fetch fails
                    result['passenger_nic'] = passenger_nic
                    result['passenger_type'] = passenger_type
                    booked_tickets_details.append(result)
            else:
                failed_bookings += 1

        if len(booked_tickets) == ticket_count:
            # All tickets booked successfully - prepare data for thermal print
            # Convert all ticket data to JSON-serializable format
            import json
            from datetime import datetime, date as date_type

            def serialize_value(value):
                """Convert any value to JSON-serializable format"""
                if value is None:
                    return None
                elif isinstance(value, (datetime, date_type)):
                    return value.isoformat()
                elif isinstance(value, (int, float, str, bool)):
                    return value
                elif isinstance(value, dict):
                    return {k: serialize_value(v) for k, v in value.items()}
                elif isinstance(value, (list, tuple)):
                    return [serialize_value(item) for item in value]
                else:
                    return str(value)

            serialized_tickets = []
            for ticket in booked_tickets_details:
                serialized_ticket = {key: serialize_value(value) for key, value in ticket.items()}
                serialized_tickets.append(serialized_ticket)

            tickets_data = {
                "tickets": serialized_tickets,
                "schedule": serialize_value(sched),
                "origin": origin,
                "destination": dest,
                "date": date,
                "class": cls
            }

            success_msg = f"✓ Successfully booked {len(booked_tickets)} ticket{'s' if len(booked_tickets) > 1 else ''}! Ticket IDs: {', '.join(booked_tickets)}"
            return success_msg, True, "success", tickets_data, True  # Open modal with success message
        elif len(booked_tickets) > 0:
            ticket_ids = ", ".join(booked_tickets)
            return f"Partially successful: {len(booked_tickets)} booked ({ticket_ids}), {failed_bookings} failed", True, "warning", None, False
        else:
            return f"All bookings failed. Please check your details and try again.", True, "danger", None, False

    @callback(
        [Output("ticket-count", "children"),
         Output("ticket-count-store", "data")],
        [Input("increase-tickets", "n_clicks"),
         Input("decrease-tickets", "n_clicks")],
        State("ticket-count-store", "data"),
        prevent_initial_call=True
    )
    def update_ticket_count(inc_clicks, dec_clicks, current_count):
        """Update ticket count (increase/decrease)"""
        ctx = callback_context
        if not ctx.triggered:
            return str(current_count), current_count
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "increase-tickets" and current_count < 10:
            new_count = current_count + 1
        elif button_id == "decrease-tickets" and current_count > 1:
            new_count = current_count - 1
        else:
            new_count = current_count
        return str(new_count), new_count

    @callback(
        [Output({"type": "passenger-type", "index": MATCH}, "value"),
         Output({"type": "passenger-type-btn-adult", "index": MATCH}, "style"),
         Output({"type": "passenger-type-btn-child", "index": MATCH}, "style"),
         Output({"type": "passenger-fields", "index": MATCH}, "children")],
        [Input({"type": "passenger-type-btn-adult", "index": MATCH}, "n_clicks"),
         Input({"type": "passenger-type-btn-child", "index": MATCH}, "n_clicks")],
        [State({"type": "passenger-type", "index": MATCH}, "value"),
         State({"type": "passenger-type", "index": MATCH}, "id")],
        prevent_initial_call=True
    )
    def toggle_passenger_type(adult_clicks, child_clicks, current_type, component_id):
        """Toggle between Adult and Child passenger type"""
        if not callback_context.triggered:
            raise PreventUpdate
        
        button_id = callback_context.triggered[0]["prop_id"].split(".")[0]
        
        # Determine which button was clicked
        if "adult" in button_id:
            new_type = "adult"
        else:
            new_type = "child"
        
        # Define button styles
        adult_style = {
            'background': COLORS['primary'] if new_type == "adult" else '#e0e0e0',
            'color': 'white' if new_type == "adult" else COLORS['text_secondary'],
            'border': 'none',
            'padding': '8px 16px',
            'borderRadius': '8px 0 0 8px',
            'cursor': 'pointer',
            'fontSize': '13px',
            'fontWeight': '500',
            'transition': 'all 0.2s',
            'flex': '1'
        }
        
        child_style = {
            'background': COLORS['primary'] if new_type == "child" else '#e0e0e0',
            'color': 'white' if new_type == "child" else COLORS['text_secondary'],
            'border': 'none',
            'padding': '8px 16px',
            'borderRadius': '0 8px 8px 0',
            'cursor': 'pointer',
            'fontSize': '13px',
            'fontWeight': '500',
            'transition': 'all 0.2s',
            'flex': '1'
        }
        
        # Get passenger index for field generation
        passenger_index = component_id.get("index", 0)
        
        # Update field requirements based on passenger type
        if new_type == "child":
            # For children, NIC/Passport is required, Contact is optional
            fields = dbc.Row([
                dbc.Col([
                    dbc.Label("NIC/Passport *", style={'fontWeight': '500', 'fontSize': '13px'}),
                    dbc.Input(
                        id={"type": "passenger-nic", "index": passenger_index},
                        placeholder="123456789V or AB1234567",
                        style={'borderRadius': '6px'}
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("Contact Number (Optional)", style={'fontWeight': '500', 'fontSize': '13px', 'color': COLORS['text_secondary']}),
                    dbc.Input(
                        id={"type": "passenger-contact", "index": passenger_index},
                        placeholder="Optional",
                        style={'borderRadius': '6px'}
                    ),
                ], width=6),
            ], className="mb-2")
        else:
            # For adults, NIC/Passport is required, Contact is optional
            fields = dbc.Row([
                dbc.Col([
                    dbc.Label("NIC/Passport *", style={'fontWeight': '500', 'fontSize': '13px'}),
                    dbc.Input(
                        id={"type": "passenger-nic", "index": passenger_index},
                        placeholder="123456789V or AB1234567",
                        style={'borderRadius': '6px'}
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("Contact Number (Optional)", style={'fontWeight': '500', 'fontSize': '13px', 'color': COLORS['text_secondary']}),
                    dbc.Input(
                        id={"type": "passenger-contact", "index": passenger_index},
                        placeholder="Optional",
                        style={'borderRadius': '6px'}
                    ),
                ], width=6),
            ], className="mb-2")
        
        return new_type, adult_style, child_style, fields

    @callback(
        Output("passenger-details-container", "children"),
        Input("ticket-count-store", "data")
    )
    def update_passenger_fields(count):
        """Generate passenger detail input fields based on ticket count"""
        if not count or count < 1:
            return html.Div()

        passenger_fields = []
        for i in range(count):
            passenger_fields.append(
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.H6(f"Passenger {i+1} Details", style={
                                'color': COLORS['text_primary'],
                                'fontWeight': '600',
                                'margin': '0'
                            })
                        ], width=6),
                        dbc.Col([
                            html.Div([
                                html.Button([
                                    html.I(className="fas fa-user", style={'marginRight': '6px'}),
                                    "Adult"
                                ], id={"type": "passenger-type-btn-adult", "index": i}, style={
                                    'background': COLORS['primary'],
                                    'color': 'white',
                                    'border': 'none',
                                    'padding': '8px 16px',
                                    'borderRadius': '8px 0 0 8px',
                                    'cursor': 'pointer',
                                    'fontSize': '13px',
                                    'fontWeight': '500',
                                    'transition': 'all 0.2s',
                                    'flex': '1'
                                }),
                                html.Button([
                                    html.I(className="fas fa-child", style={'marginRight': '6px'}),
                                    "Child"
                                ], id={"type": "passenger-type-btn-child", "index": i}, style={
                                    'background': '#e0e0e0',
                                    'color': COLORS['text_secondary'],
                                    'border': 'none',
                                    'padding': '8px 16px',
                                    'borderRadius': '0 8px 8px 0',
                                    'cursor': 'pointer',
                                    'fontSize': '13px',
                                    'fontWeight': '500',
                                    'transition': 'all 0.2s',
                                    'flex': '1'
                                }),
                                dbc.RadioItems(
                                    id={"type": "passenger-type", "index": i},
                                    options=[
                                        {"label": " Adult", "value": "adult"},
                                        {"label": " Child", "value": "child"}
                                    ],
                                    value="adult",
                                    inline=True,
                                    style={'display': 'none'}
                                )
                            ], style={'display': 'flex', 'gap': '0'})
                        ], width=6, style={'textAlign': 'right'})
                    ], style={
                        'marginTop': '16px',
                        'marginBottom': '12px',
                        'paddingTop': '12px',
                        'borderTop': f'1px solid {COLORS["border"]}' if i > 0 else 'none'
                    }),
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("NIC/Passport *", style={'fontWeight': '500', 'fontSize': '13px'}),
                                dbc.Input(
                                    id={"type": "passenger-nic", "index": i},
                                    placeholder="123456789V or AB1234567",
                                    style={'borderRadius': '6px'}
                                ),
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Contact Number", style={'fontWeight': '500', 'fontSize': '13px'}),
                                dbc.Input(
                                    id={"type": "passenger-contact", "index": i},
                                    placeholder="0712345678",
                                    style={'borderRadius': '6px'}
                                ),
                            ], width=6),
                        ], className="mb-2")
                    ], id={"type": "passenger-fields", "index": i})
                ])
            )
        return html.Div(passenger_fields)

    @callback(
        Output("thermal-print-content", "children"),
        Input("booked-tickets-store", "data"),
        prevent_initial_call=True
    )
    def generate_thermal_print(tickets_data):
        """Generate thermal print style ticket"""
        if not tickets_data or "tickets" not in tickets_data:
            return html.Div("No ticket data available")
        
        tickets = tickets_data.get("tickets", [])

        # Get station names and train schedule from API
        origin_id = tickets_data.get("origin")
        dest_id = tickets_data.get("destination")

        # Get schedule_id from the first ticket to fetch train schedule details
        schedule_id = tickets[0].get("schedule_id") if tickets else None

        origin_station = make_api_request(f"/stations/{origin_id}", token=None) if origin_id else {}
        dest_station = make_api_request(f"/stations/{dest_id}", token=None) if dest_id else {}
        train_schedule = make_api_request(f"/schedules/{schedule_id}", token=None) if schedule_id else {}

        origin_name = origin_station.get("station_name", origin_id) if origin_station else origin_id
        dest_name = dest_station.get("station_name", dest_id) if dest_station else dest_id
        train_name = train_schedule.get("train_schedule", "N/A") if train_schedule else "N/A"
        
        # Create thermal print style for each ticket
        ticket_components = []
        
        for idx, ticket in enumerate(tickets):
            if idx > 0:
                ticket_components.append(html.Hr(style={
                    'border': 'none',
                    'borderTop': '2px dashed #999',
                    'margin': '20px 0'
                }))
            
            ticket_components.append(
                html.Div([
                    # Header
                    html.Div([
                        html.Div("SRI LANKA RAILWAYS", style={
                            'fontSize': '18px',
                            'fontWeight': 'bold',
                            'textAlign': 'center',
                            'marginBottom': '5px'
                        }),
                        html.Div("TRAIN TICKET", style={
                            'fontSize': '14px',
                            'textAlign': 'center',
                            'marginBottom': '10px'
                        }),
                        html.Div("=" * 38, style={
                            'textAlign': 'center',
                            'marginBottom': '10px',
                            'overflow': 'hidden',
                            'whiteSpace': 'nowrap'
                        }),
                    ]),
                    
                    # Ticket ID
                    html.Div([
                        html.Div(f"TICKET ID: {ticket.get('ticket_id', 'N/A')}", style={
                            'fontSize': '13px',
                            'fontWeight': 'bold',
                            'marginBottom': '5px'
                        }),
                        html.Div(f"Issue Date: {ticket.get('issue_date', 'N/A')}", style={
                            'fontSize': '12px',
                            'marginBottom': '10px'
                        }),
                    ]),
                    
                    # Journey Details
                    html.Div([
                        html.Div(f"From: {origin_name}", style={'fontSize': '12px', 'marginBottom': '3px'}),
                        html.Div(f"To:   {dest_name}", style={'fontSize': '12px', 'marginBottom': '3px'}),
                        html.Div(f"Train: {train_name}", style={'fontSize': '12px', 'marginBottom': '3px'}),
                        html.Div(f"Date: {tickets_data.get('date', 'N/A')}", style={'fontSize': '12px', 'marginBottom': '10px'}),
                    ]),
                    
                    # Time Details
                    html.Div([
                        html.Div(f"Departure: {ticket.get('origin_departure', 'N/A')}", style={
                            'fontSize': '12px',
                            'marginBottom': '3px'
                        }),
                        html.Div(f"Arrival:   {ticket.get('destination_departure', 'N/A')}", style={
                            'fontSize': '12px',
                            'marginBottom': '10px'
                        }),
                    ]),
                    
                    # Passenger Details
                    html.Div([
                        html.Div(f"Class: {ticket.get('class', 'N/A')}", style={'fontSize': '12px', 'marginBottom': '3px'}),
                        html.Div(f"Type: {ticket.get('passenger_type', 'adult').upper()}", style={
                            'fontSize': '12px',
                            'marginBottom': '3px'
                        }),
                        html.Div(f"NIC/Passport: {ticket.get('passenger_nic', 'N/A')}", style={
                            'fontSize': '12px',
                            'marginBottom': '3px'
                        }),
                        html.Div(f"Contact: {ticket.get('contact_number', 'N/A')}", style={
                            'fontSize': '12px',
                            'marginBottom': '10px'
                        }),
                    ]),
                    
                    # Payment Details
                    html.Div([
                        html.Div("-" * 38, style={
                            'marginBottom': '5px',
                            'overflow': 'hidden',
                            'whiteSpace': 'nowrap'
                        }),
                        html.Div(f"FARE: LKR {float(ticket.get('fee', 0)):.2f}", style={
                            'fontSize': '14px',
                            'fontWeight': 'bold',
                            'textAlign': 'right',
                            'marginBottom': '5px'
                        }),
                        html.Div(f"Payment: {ticket.get('payment_method', 'N/A')}", style={
                            'fontSize': '12px',
                            'marginBottom': '3px'
                        }),
                        html.Div(f"Status: {ticket.get('status', 'N/A')}", style={
                            'fontSize': '12px',
                            'marginBottom': '10px'
                        }),
                    ]),
                    
                    # Footer
                    html.Div([
                        html.Div("=" * 38, style={
                            'marginBottom': '5px',
                            'overflow': 'hidden',
                            'whiteSpace': 'nowrap'
                        }),
                        html.Div("Please arrive 15 minutes before", style={
                            'fontSize': '10px',
                            'textAlign': 'center',
                            'marginBottom': '3px'
                        }),
                        html.Div("departure time", style={
                            'fontSize': '10px',
                            'textAlign': 'center',
                            'marginBottom': '5px'
                        }),
                        html.Div("Thank you for choosing", style={
                            'fontSize': '10px',
                            'textAlign': 'center',
                            'marginBottom': '3px'
                        }),
                        html.Div("Sri Lanka Railways", style={
                            'fontSize': '10px',
                            'textAlign': 'center'
                        }),
                    ])
                ], style={
                    'border': '2px solid #000',
                    'padding': '15px',
                    'background': 'white'
                })
            )
        
        return html.Div(ticket_components)

    @callback(
        Output("ticket-print-modal", "is_open", allow_duplicate=True),
        Input("close-ticket-modal", "n_clicks"),
        State("ticket-print-modal", "is_open"),
        prevent_initial_call=True
    )
    def close_thermal_modal(n, is_open):
        """Close the thermal print modal"""
        if n:
            return False
        return is_open
