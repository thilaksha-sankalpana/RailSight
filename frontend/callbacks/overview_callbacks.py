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
            create_stat_card("fas fa-train", "0", "Trains Active Today", COLORS['primary']),
            create_stat_card("fas fa-calendar-check", "0", "Trains Scheduled Today", COLORS['info']),
            create_stat_card("fas fa-ticket-alt", "0", "Tickets Booked Today", COLORS['success']),
            create_stat_card("fas fa-dollar-sign", "LKR 0", "Revenue Today", COLORS['warning'])
        ]
        if not token or pathname != "/":
            return default
        data = make_api_request("/analytics/summary", token=token, timeout=10)
        if data:
            return [
                create_stat_card("fas fa-train", str(data.get("trains_active_today", 0)),
                               "Trains Active Today", COLORS['primary']),
                create_stat_card("fas fa-calendar-check", str(data.get("trains_scheduled_today", 0)),
                               "Trains Scheduled Today", COLORS['info']),
                create_stat_card("fas fa-ticket-alt", str(data.get("total_tickets_today", 0)),
                               "Tickets Booked Today", COLORS['success']),
                create_stat_card("fas fa-dollar-sign", f"LKR {float(data.get('revenue_today', 0)):,.2f}",
                               "Revenue Today", COLORS['warning'])
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
                line=dict(color=COLORS['primary'], width=3),
                marker=dict(size=8, color=COLORS['primary']),
                fill='tozeroy',
                fillcolor=f'rgba(196, 30, 58, 0.1)',
                name='Tickets Sold'
            ))
            fig.update_layout(
                template="plotly_white",
                height=280,
                margin=dict(l=40, r=20, t=10, b=40),
                xaxis=dict(
                    title="Date",
                    showgrid=False
                ),
                yaxis=dict(
                    title="Number of Tickets",
                    showgrid=True,
                    gridcolor='#f1f5f9'
                ),
                hovermode='x unified',
                showlegend=False
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
            labels = ['Completed', 'Pending']
            values = [data.get('completed', 0), data.get('pending', 0)]
            colors_pie = [COLORS['success'], COLORS['warning']]
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors_pie),
                hole=0.4,
                textinfo='label+percent+value',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>Schedules: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            fig.update_layout(
                template="plotly_white",
                height=280,
                margin=dict(l=20, r=20, t=10, b=20),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
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
            labels = ['1st Class', '2nd Class', '3rd Class']
            values = [
                data.get('first_class', 0),
                data.get('second_class', 0),
                data.get('third_class', 0)
            ]
            colors_pie = [COLORS['primary'], COLORS['info'], COLORS['success']]
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors_pie),
                hole=0.4,
                textinfo='label+percent+value',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>Tickets: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            fig.update_layout(
                template="plotly_white",
                height=280,
                margin=dict(l=20, r=20, t=10, b=20),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )
        return fig
