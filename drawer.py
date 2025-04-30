import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import streamlit as st
from pandas import DataFrame
from streamlit import plotly_chart

def draw_sale_history(sale_history: DataFrame) -> None:
    if not sale_history.empty:
        max_range_y = np.ceil(max(sale_history["qty"]) * 1.15)
        fig = px.line(sale_history, x="date", y="qty", range_y=[0, max_range_y])
        plotly_chart(fig)
    else:
        st.subheader("No current sales")

def draw_resell_listings(listings: DataFrame, world_label: str, total_label: str, unit_label: str, title_label: str) -> None:
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