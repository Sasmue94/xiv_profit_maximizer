# this module is made for drawing any needed visualisations of data on screen

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import streamlit as st
from pandas import DataFrame
from streamlit import plotly_chart

# draw line graph of sales history on screen
def draw_sale_history(sale_history: DataFrame) -> None:
    """
    draws line chart of requested sale history of item on current world \n
    :param sale_history: DataFrame containing the last saved sales history of an items
    :return: None
    """
    if not sale_history.empty:
        max_range_y = np.ceil(max(sale_history["qty"]) * 1.15)
        fig = px.line(sale_history, x="date", y="qty", range_y=[0, max_range_y])
        plotly_chart(fig)
    else:
        st.subheader("No current sales")

# draw bar chart of the most fitting, cheapes listings of an item across all worlds of a given Datacenter
def draw_resell_listings(listings: DataFrame, world_label: str, total_label: str, unit_label: str, title_label: str) -> None:
    """
    draws bar chart of requested listings across all worlds on the Datacenter \n
    :param listings: DataFrame containing current item listings on market boards
    :param labels: strings containing information to display in the bar chart
    :return: None
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=listings["world"], y=listings["total"], name=total_label, width=0.5),
        secondary_y=False,

    )

    fig.add_trace(
        go.Bar(x=listings["world"], y=listings["price_per_unit"], name=unit_label, width=0.5, offset=0.05),
        secondary_y=True
    )

    fig.update_layout(title_text=title_label, legend_title_text="Costs", xaxis_title=world_label)

    fig.update_xaxes(title_text=world_label,)
    fig.update_yaxes(title_text=total_label, secondary_y=False)
    fig.update_yaxes(title_text=unit_label, secondary_y=True)
    plotly_chart(fig)