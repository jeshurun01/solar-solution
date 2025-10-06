"""
Chart generation utilities for Solar Solution.

This module contains functions to create interactive Plotly charts for
visualizing energy consumption, power profiles, and hourly patterns.
"""

from typing import Dict, Any, TYPE_CHECKING
import plotly.express as px
import plotly.graph_objects as go

if TYPE_CHECKING:
    from models import EquipmentFactory


def create_consumption_pie_chart(factory: "EquipmentFactory", t: Dict[str, Any]) -> go.Figure:
    """
    Create a pie chart showing energy consumption distribution by equipment.
    
    Args:
        factory: EquipmentFactory instance with equipment data
        t: Translation dictionary
        
    Returns:
        go.Figure: Plotly figure with pie chart
    """
    df = factory.df_datas()
    fig = px.pie(
        df,
        values="Energie",
        names="Name",
        title=t["Charts"]["consumption_subtitle"],
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=True, height=400)
    return fig


def create_power_time_chart(factory: "EquipmentFactory", t: Dict[str, Any]) -> go.Figure:
    """
    Create a grouped bar chart showing power and time for each equipment.
    
    Uses dual y-axes to display both power (W) and usage time (h) on the
    same chart with different scales.
    
    Args:
        factory: EquipmentFactory instance with equipment data
        t: Translation dictionary
        
    Returns:
        go.Figure: Plotly figure with grouped bar chart
    """
    df = factory.df_datas()
    
    fig = go.Figure()
    
    # Add power bars
    fig.add_trace(go.Bar(
        name=t["Charts"]["power"],
        x=df["Name"],
        y=df["Power"],
        marker_color='lightblue',
        yaxis='y',
        offsetgroup=1
    ))
    
    # Add time bars
    fig.add_trace(go.Bar(
        name=t["Charts"]["time"],
        x=df["Name"],
        y=df["Usage Time"],
        marker_color='lightcoral',
        yaxis='y2',
        offsetgroup=2
    ))
    
    fig.update_layout(
        title=t["Charts"]["power_time_title"],
        xaxis=dict(title=t["Charts"]["equipment"]),
        yaxis=dict(title=t["Charts"]["power"], side='left'),
        yaxis2=dict(title=t["Charts"]["time"], overlaying='y', side='right'),
        barmode='group',
        height=400,
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig


def create_hourly_profile_chart(factory: "EquipmentFactory", t: Dict[str, Any]) -> go.Figure:
    """
    Create an interactive line chart showing hourly consumption profile over 24 hours.
    
    The chart includes:
    - Area chart for total consumption
    - Individual equipment traces (hidden by default)
    - Peak consumption line with annotation
    - Average consumption line with annotation
    
    Args:
        factory: EquipmentFactory instance with equipment data
        t: Translation dictionary
        
    Returns:
        go.Figure: Plotly figure with hourly profile chart
    """
    hourly_profile = factory.get_hourly_profile()
    hours = list(range(24))
    
    fig = go.Figure()
    
    # Add area chart for total consumption
    fig.add_trace(go.Scatter(
        x=hours,
        y=hourly_profile,
        mode='lines',
        name=t["Hourly"]["consumption"],
        fill='tozeroy',
        line=dict(color='rgb(255, 127, 14)', width=3),
        hovertemplate='<b>%{x}h</b><br>%{y:.0f} W<extra></extra>'
    ))
    
    # Add individual equipment traces
    colors = px.colors.qualitative.Set2
    for idx, equipment in enumerate(factory.get_equipments()):
        hourly = equipment.get_hourly_consumption()
        fig.add_trace(go.Scatter(
            x=hours,
            y=hourly,
            mode='lines',
            name=equipment.name,
            line=dict(color=colors[idx % len(colors)], width=1, dash='dot'),
            visible='legendonly',  # Hidden by default
            hovertemplate=f'<b>{equipment.name}</b><br>%{{x}}h: %{{y:.0f}} W<extra></extra>'
        ))
    
    # Calculate peak and average
    peak_consumption = max(hourly_profile) if hourly_profile else 0
    avg_consumption = sum(hourly_profile) / 24 if hourly_profile else 0
    peak_hour = hourly_profile.index(peak_consumption) if peak_consumption > 0 else 0
    
    # Add peak line
    fig.add_hline(
        y=peak_consumption,
        line_dash="dash",
        line_color="red",
        annotation_text=f"{t['Hourly']['peak_consumption']}: {peak_consumption:.0f}W @ {peak_hour}h",
        annotation_position="top right"
    )
    
    # Add average line
    fig.add_hline(
        y=avg_consumption,
        line_dash="dash",
        line_color="green",
        annotation_text=f"{t['Hourly']['average_consumption']}: {avg_consumption:.0f}W",
        annotation_position="bottom right"
    )
    
    fig.update_layout(
        title=t["Hourly"]["chart_title"],
        xaxis=dict(
            title=t["Hourly"]["hour"],
            tickmode='linear',
            tick0=0,
            dtick=2,
            range=[-0.5, 23.5]
        ),
        yaxis=dict(title=t["Hourly"]["consumption"]),
        height=500,
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig
