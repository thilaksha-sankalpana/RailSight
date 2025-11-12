"""
TCDAFS - Pricing Callbacks
Handle ticket pricing management
"""
from dash import callback, Input, Output, State, html, no_update, ALL, callback_context
import dash_bootstrap_components as dbc
from utils.api import make_api_request
from config.styles import COLORS
import logging

logger = logging.getLogger(__name__)


def register(app):
    """Register pricing callbacks with the app"""

    def search_stations(search_value, token):
        """Search stations with server-side filtering"""
        if not token:
            return []
        
        try:
            if search_value and len(search_value) >= 2:
                endpoint = f"/stations?search={search_value}&limit=50"
            else:
                endpoint = "/stations?limit=50"
            
            stations = make_api_request(endpoint, token=token, timeout=10)
            if stations and isinstance(stations, list):
                return [{"label": s.get("station_name", "Unknown"), "value": s.get("station_id", "")} 
                       for s in stations]
        except Exception as e:
            logger.error(f"Error searching stations: {e}")
        return []

    @callback(
        Output("filter-pricing-origin", "options"),
        [Input("url", "pathname"),
         Input("filter-pricing-origin", "search_value"),
         Input("token-store", "data")],
        prevent_initial_call=False
    )
    def load_pricing_origin_stations(pathname, search_value, token):
        """Load origin stations for pricing filters with search"""
        if pathname != "/pricing":
            return []
        return search_stations(search_value, token)

    @callback(
        Output("filter-pricing-destination", "options"),
        [Input("url", "pathname"),
         Input("filter-pricing-origin", "value"),
         Input("filter-pricing-destination", "search_value"),
         Input("token-store", "data")],
        [State("filter-pricing-destination", "value")],
        prevent_initial_call=False
    )
    def load_pricing_destination_stations(pathname, origin_value, search_value, token, current_value):
        """Load destination stations for pricing filters with search, excluding selected origin"""
        if pathname != "/pricing":
            return []
        
        stations_opts = search_stations(search_value, token)
        
        # Exclude the origin station from destination options
        opts = [opt for opt in stations_opts if opt["value"] != origin_value]
        
        # If there's a current selection not in the new options and it's not the origin, add it back
        if current_value and current_value != origin_value:
            existing_values = [opt["value"] for opt in opts]
            if current_value not in existing_values:
                try:
                    selected_station = make_api_request(f"/stations/{current_value}", token=token, timeout=5)
                    if selected_station and isinstance(selected_station, dict):
                        opts.insert(0, {"label": selected_station.get("station_name", "Unknown"),
                                       "value": selected_station.get("station_id", "")})
                except Exception as e:
                    logger.error(f"Error fetching current station: {e}")
        
        return opts

    @callback(
        [Output("filter-pricing-origin", "value"),
         Output("filter-pricing-destination", "value")],
        Input("clear-pricing-filter", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_pricing_filters(n_clicks):
        """Reset pricing filter dropdowns when clear button is clicked"""
        if n_clicks:
            return None, None
        return no_update, no_update

    @callback(
        Output("pricing-table", "children"),
        [Input("apply-pricing-filter", "n_clicks"),
         Input("clear-pricing-filter", "n_clicks")],
        [State("filter-pricing-origin", "value"),
         State("filter-pricing-destination", "value"),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def load_pricing_table(apply_clicks, clear_clicks, origin, destination, token):
        """Load ticket pricing table from train_station_ticket_prices - only when filter is applied"""
        if not token:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle", style={'fontSize': '48px', 'color': COLORS['warning'], 'opacity': '0.3', 'marginBottom': '16px'}),
                    html.H5("Authentication Required", style={'color': COLORS['text_secondary'], 'fontWeight': '500'}),
                    html.P("Please login to view pricing data", style={'color': COLORS['text_secondary'], 'fontSize': '14px', 'marginTop': '8px'})
                ], style={'textAlign': 'center', 'padding': '80px 20px'})
            ])

        # Show instruction message if no filter applied yet
        if not apply_clicks and not clear_clicks:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-search-dollar", style={'fontSize': '64px', 'color': COLORS['primary'], 'opacity': '0.2', 'marginBottom': '24px'}),
                    html.H4("Search for Ticket Pricing", style={'color': COLORS['text_primary'], 'fontWeight': '600', 'marginBottom': '12px'}),
                    html.P("Use the filters above to search for pricing between stations", style={'color': COLORS['text_secondary'], 'fontSize': '15px', 'marginBottom': '8px'}),
                    html.Div([
                        html.I(className="fas fa-info-circle", style={'marginRight': '8px', 'color': COLORS['info']}),
                        html.Span("You can filter by origin station, destination station, or both", style={'fontSize': '14px', 'color': COLORS['text_secondary']})
                    ], style={'marginTop': '16px'})
                ], style={'textAlign': 'center', 'padding': '100px 40px'})
            ])

        # Build query parameters
        params = []
        if origin:
            params.append(f"origin={origin}")
        if destination:
            params.append(f"destination={destination}")
        
        endpoint = "/prices"
        if params:
            endpoint += "?" + "&".join(params)
        
        # Fetch pricing data
        prices = make_api_request(endpoint, token=token, timeout=10)
        
        if not prices or not isinstance(prices, list):
            return html.Div([
                html.Div([
                    html.I(className="fas fa-inbox", style={'fontSize': '56px', 'color': COLORS['text_secondary'], 'opacity': '0.2', 'marginBottom': '20px'}),
                    html.H5("No Pricing Records Found", style={'fontSize': '18px', 'color': COLORS['text_secondary'], 'fontWeight': '600', 'marginBottom': '8px'}),
                    html.P("Try adjusting your filters to see pricing data", style={'fontSize': '14px', 'color': COLORS['text_secondary']})
                ], style={'textAlign': 'center', 'padding': '80px 20px'})
            ])
        
        # Create table
        table_header = html.Thead(html.Tr([
            html.Th("ID", style={'padding': '12px', 'textAlign': 'left'}),
            html.Th("Origin Station", style={'padding': '12px', 'textAlign': 'left'}),
            html.Th("Destination Station", style={'padding': '12px', 'textAlign': 'left'}),
            html.Th("Distance (km)", style={'padding': '12px', 'textAlign': 'center'}),
            html.Th("1st Class", style={'padding': '12px', 'textAlign': 'right'}),
            html.Th("2nd Class", style={'padding': '12px', 'textAlign': 'right'}),
            html.Th("3rd Class", style={'padding': '12px', 'textAlign': 'right'}),
            html.Th("Effective From", style={'padding': '12px', 'textAlign': 'center'}),
            html.Th("Effective To", style={'padding': '12px', 'textAlign': 'center'}),
            html.Th("Actions", style={'padding': '12px', 'textAlign': 'center'}),
        ]))
        
        table_rows = []
        for idx, price in enumerate(prices):
            row_style = {
                'backgroundColor': '#ffffff' if idx % 2 == 0 else '#f8f9fa',
                'borderBottom': f'1px solid {COLORS["border"]}'
            }
            
            table_rows.append(html.Tr([
                html.Td(price.get('id', 'N/A'), style={'padding': '12px'}),
                html.Td([
                    html.I(className="fas fa-map-marker-alt", style={'marginRight': '6px', 'color': '#059669', 'fontSize': '12px'}),
                    price.get('origin_station_name', 'N/A')
                ], style={'padding': '12px'}),
                html.Td([
                    html.I(className="fas fa-map-marker-alt", style={'marginRight': '6px', 'color': '#dc2626', 'fontSize': '12px'}),
                    price.get('destination_station_name', 'N/A')
                ], style={'padding': '12px'}),
                html.Td(f"{float(price.get('distance', 0)):.1f}" if price.get('distance') else 'N/A', style={'padding': '12px', 'textAlign': 'center'}),
                html.Td(f"LKR {float(price.get('first_class_fee', 0)):.2f}" if price.get('first_class_fee') else 'N/A', style={'padding': '12px', 'textAlign': 'right', 'fontWeight': '600'}),
                html.Td(f"LKR {float(price.get('second_class_fee', 0)):.2f}" if price.get('second_class_fee') else 'N/A', style={'padding': '12px', 'textAlign': 'right', 'fontWeight': '600'}),
                html.Td(f"LKR {float(price.get('third_class_fee', 0)):.2f}" if price.get('third_class_fee') else 'N/A', style={'padding': '12px', 'textAlign': 'right', 'fontWeight': '600'}),
                html.Td(price.get('effective_from', 'N/A'), style={'padding': '12px', 'textAlign': 'center', 'fontSize': '13px'}),
                html.Td(price.get('effective_to', 'No expiry'), style={'padding': '12px', 'textAlign': 'center', 'fontSize': '13px'}),
                html.Td([
                    dbc.Button([
                        html.I(className="fas fa-edit", style={'marginRight': '6px'}),
                        "Edit"
                    ], id={'type': 'edit-pricing-btn', 'index': price.get('id')}, 
                    color="primary", size="sm", outline=True),
                ], style={'padding': '12px', 'textAlign': 'center'}),
            ], style=row_style))
        
        table_body = html.Tbody(table_rows)
        
        return html.Div([
            dbc.Table([table_header, table_body], bordered=True, hover=True, responsive=True, striped=False, style={
                'marginBottom': '0',
                'fontSize': '14px'
            }),
            html.Div([
                html.I(className="fas fa-ticket-alt", style={'marginRight': '8px', 'fontSize': '13px', 'color': COLORS['primary']}),
                html.Span(f"{len(prices)} pricing record(s) found", style={'fontSize': '13px', 'color': COLORS['text_secondary'], 'fontWeight': '500'})
            ], style={'padding': '14px 20px', 'background': 'linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%)', 'borderTop': f'2px solid {COLORS["border"]}', 'textAlign': 'center'})
        ])

    @callback(
        [Output("edit-pricing-modal", "is_open"),
         Output("edit-pricing-id", "children"),
         Output("edit-pricing-origin-name", "children"),
         Output("edit-pricing-destination-name", "children"),
         Output("edit-pricing-distance", "value"),
         Output("edit-pricing-first-class", "value"),
         Output("edit-pricing-second-class", "value"),
         Output("edit-pricing-third-class", "value"),
         Output("edit-pricing-alert", "children")],
        [Input({"type": "edit-pricing-btn", "index": ALL}, "n_clicks"),
         Input("cancel-edit-pricing-btn", "n_clicks"),
         Input("save-edit-pricing-btn", "n_clicks")],
        [State({"type": "edit-pricing-btn", "index": ALL}, "id"),
         State("edit-pricing-id", "children"),
         State("edit-pricing-distance", "value"),
         State("edit-pricing-first-class", "value"),
         State("edit-pricing-second-class", "value"),
         State("edit-pricing-third-class", "value"),
         State("token-store", "data")],
        prevent_initial_call=True
    )
    def handle_edit_pricing_modal(edit_clicks, cancel_clicks, save_clicks, edit_ids, 
                                   pricing_id, distance, first_class, second_class, third_class, token):
        """Handle opening and closing the edit pricing modal"""
        ctx = callback_context
        if not ctx.triggered:
            return False, None, "", "", None, None, None, None, None
        
        trigger_id = ctx.triggered[0]["prop_id"]
        
        # Cancel button clicked
        if "cancel-edit-pricing-btn" in trigger_id:
            return False, None, "", "", None, None, None, None, None
        
        # Save button clicked
        if "save-edit-pricing-btn" in trigger_id:
            if not pricing_id or not token:
                return True, pricing_id, no_update, no_update, no_update, no_update, no_update, no_update, \
                       dbc.Alert("Error: Missing pricing ID or authentication", color="danger", dismissable=True)
            
            # Validate inputs
            if not all([distance, first_class, second_class, third_class]):
                return True, pricing_id, no_update, no_update, no_update, no_update, no_update, no_update, \
                       dbc.Alert("Please fill in all required fields", color="warning", dismissable=True)
            
            try:
                # Update pricing
                update_data = {
                    "distance": float(distance),
                    "first_class_fee": float(first_class),
                    "second_class_fee": float(second_class),
                    "third_class_fee": float(third_class)
                }
                
                result = make_api_request(f"/prices/{pricing_id}", method="PATCH", data=update_data, token=token, timeout=10)
                
                if result:
                    return False, None, "", "", None, None, None, None, \
                           dbc.Alert("Pricing updated successfully!", color="success", dismissable=True, duration=3000)
                else:
                    return True, pricing_id, no_update, no_update, no_update, no_update, no_update, no_update, \
                           dbc.Alert("Failed to update pricing", color="danger", dismissable=True)
            except Exception as e:
                logger.error(f"Error updating pricing: {e}")
                return True, pricing_id, no_update, no_update, no_update, no_update, no_update, no_update, \
                       dbc.Alert(f"Error: {str(e)}", color="danger", dismissable=True)
        
        # Edit button clicked
        if "edit-pricing-btn" in trigger_id:
            if not any(edit_clicks) or all(click is None for click in edit_clicks):
                return False, None, "", "", None, None, None, None, None
            
            # Find which button was clicked
            clicked_index = None
            for i, clicks in enumerate(edit_clicks):
                if clicks:
                    clicked_index = i
                    break
            
            if clicked_index is not None and clicked_index < len(edit_ids):
                price_id = edit_ids[clicked_index]["index"]
                
                try:
                    price_data = make_api_request(f"/prices/{price_id}", token=token, timeout=10)
                    if price_data:
                        return True, price_id, \
                               price_data.get('origin_station_name', 'N/A'), \
                               price_data.get('destination_station_name', 'N/A'), \
                               float(price_data.get('distance', 0)), \
                               float(price_data.get('first_class_fee', 0)), \
                               float(price_data.get('second_class_fee', 0)), \
                               float(price_data.get('third_class_fee', 0)), \
                               None
                except Exception as e:
                    logger.error(f"Error fetching pricing details: {e}")
                    return False, None, "", "", None, None, None, None, \
                           dbc.Alert(f"Error loading pricing: {str(e)}", color="danger", dismissable=True)
        
        return False, None, "", "", None, None, None, None, None
