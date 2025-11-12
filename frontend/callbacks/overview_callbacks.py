"""
TCDAFS - Overview/Dashboard Callbacks
Handle dashboard KPI updates and chart rendering
"""
from dash import callback, Input, Output, State
from utils.api import make_api_request
from config.styles import COLORS
from components.common.stat_card import create_stat_card
import plotly.graph_objects as go
import logging

logger = logging.getLogger(__name__)


def register(app):
    """Register overview/dashboard callbacks with the app"""

    @callback(
        [Output("stat-card-1", "children"),
         Output("stat-card-2", "children"),
         Output("stat-card-3", "children"),
         Output("stat-card-4", "children")],
        [Input("overview-interval", "n_intervals"),
         Input("url", "pathname")],
        State("token-store", "data")
    )
    def update_stats(n, pathname, token):
        """
        Update KPI stat cards with real-time analytics

        Args:
            n: Interval counter
            pathname: Current URL pathname
            token: Authentication token data

        Returns:
            Tuple of 4 stat card components
        """
        default = [
            create_stat_card("fas fa-train", "0", "Active Train Operations", COLORS['primary']),
            create_stat_card("fas fa-calendar-check", "0", "Scheduled Services Today", COLORS['info']),
            create_stat_card("fas fa-ticket-alt", "0", "Total Bookings Today", COLORS['success']),
            create_stat_card("fas fa-dollar-sign", "LKR 0", "Daily Revenue Generated", COLORS['warning'])
        ]
        if not token or pathname != "/":
            return default
        data = make_api_request("/analytics/summary", token=token, timeout=10)
        if data:
            return [
                create_stat_card("fas fa-train", str(data.get("trains_active_today", 0)),
                               "Active Train Operations", COLORS['primary']),
                create_stat_card("fas fa-calendar-check", str(data.get("trains_scheduled_today", 0)),
                               "Scheduled Services Today", COLORS['info']),
                create_stat_card("fas fa-ticket-alt", str(data.get("total_tickets_today", 0)),
                               "Total Bookings Today", COLORS['success']),
                create_stat_card("fas fa-dollar-sign", f"LKR {float(data.get('revenue_today', 0)):,.2f}",
                               "Daily Revenue Generated", COLORS['warning'])
            ]
        return default

    @callback(
        Output("daily-ticket-sales-chart", "figure"),
        [Input("overview-interval", "n_intervals"),
         Input("url", "pathname")],
        State("token-store", "data")
    )
    def update_daily_ticket_sales_chart(n, pathname, token):
        """
        Update daily ticket sales chart with historical data

        Args:
            n: Interval counter
            pathname: Current URL pathname
            token: Authentication token data

        Returns:
            Plotly figure with ticket sales trend
        """
        fig = go.Figure()
        if not token or pathname != "/":
            return fig
        data = make_api_request("/analytics/daily-ticket-sales", token=token, timeout=10)
        if data:
            fig.add_trace(go.Scatter(
                x=data.get("dates", []),
                y=data.get("tickets", []),
                mode='lines+markers',
                line=dict(color=COLORS['primary'], width=3, shape='spline'),
                marker=dict(size=8, color=COLORS['primary'], line=dict(width=2, color='white')),
                fill='tozeroy',
                fillcolor=f'rgba(196, 30, 58, 0.1)',
                name='Tickets Sold',
                hovertemplate='<b>Date:</b> %{x}<br><b>Bookings:</b> %{y}<extra></extra>'
            ))
            fig.update_layout(
                template="plotly_white",
                height=280,
                margin=dict(l=50, r=20, t=10, b=50),
                xaxis=dict(
                    title="<b>Date Period</b>",
                    showgrid=False,
                    title_font=dict(size=13, color=COLORS['text_secondary'])
                ),
                yaxis=dict(
                    title="<b>Total Bookings</b>",
                    showgrid=True,
                    gridcolor='#f1f5f9',
                    title_font=dict(size=13, color=COLORS['text_secondary'])
                ),
                hovermode='x unified',
                showlegend=False,
                font=dict(family="Inter, system-ui, sans-serif")
            )
        return fig

    @callback(
        Output("schedule-status-pie", "figure"),
        [Input("overview-interval", "n_intervals"),
         Input("url", "pathname")],
        State("token-store", "data")
    )
    def update_schedule_status_pie(n, pathname, token):
        """
        Update schedule status pie chart (completed vs pending)

        Args:
            n: Interval counter
            pathname: Current URL pathname
            token: Authentication token data

        Returns:
            Plotly pie chart figure
        """
        fig = go.Figure()
        if not token or pathname != "/":
            return fig
        data = make_api_request("/analytics/schedule-status-today", token=token, timeout=10)
        if data:
            labels = ['Completed Services', 'Pending Services']
            values = [data.get('completed', 0), data.get('pending', 0)]
            colors_pie = [COLORS['success'], COLORS['warning']]
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker=dict(
                    colors=colors_pie,
                    line=dict(color='white', width=3)
                ),
                hole=0.45,
                textinfo='label+percent',
                textposition='auto',
                textfont=dict(size=12, color='white', family='Inter, system-ui, sans-serif'),
                hovertemplate='<b>%{label}</b><br>Count: %{value} services<br>Share: %{percent}<extra></extra>'
            )])
            fig.update_layout(
                template="plotly_white",
                height=280,
                margin=dict(l=20, r=20, t=10, b=20),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11, family='Inter, system-ui, sans-serif')
                ),
                font=dict(family="Inter, system-ui, sans-serif")
            )
        return fig

    @callback(
        Output("class-distribution-pie", "figure"),
        [Input("overview-interval", "n_intervals"),
         Input("url", "pathname")],
        State("token-store", "data")
    )
    def update_class_distribution_pie(n, pathname, token):
        """
        Update class distribution pie chart (1st/2nd/3rd class ticket distribution)

        Args:
            n: Interval counter
            pathname: Current URL pathname
            token: Authentication token data

        Returns:
            Plotly pie chart figure
        """
        fig = go.Figure()
        if not token or pathname != "/":
            return fig
        data = make_api_request("/analytics/class-distribution-today", token=token, timeout=10)
        if data:
            labels = ['First Class Premium', 'Second Class Standard', 'Third Class Economy']
            values = [
                data.get('first_class', 0),
                data.get('second_class', 0),
                data.get('third_class', 0)
            ]
            colors_pie = [COLORS['primary'], COLORS['info'], COLORS['success']]
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker=dict(
                    colors=colors_pie,
                    line=dict(color='white', width=3)
                ),
                hole=0.45,
                textinfo='label+percent',
                textposition='auto',
                textfont=dict(size=12, color='white', family='Inter, system-ui, sans-serif'),
                hovertemplate='<b>%{label}</b><br>Bookings: %{value} tickets<br>Share: %{percent}<extra></extra>'
            )])
            fig.update_layout(
                template="plotly_white",
                height=280,
                margin=dict(l=20, r=20, t=10, b=20),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11, family='Inter, system-ui, sans-serif')
                ),
                font=dict(family="Inter, system-ui, sans-serif")
            )
        return fig
