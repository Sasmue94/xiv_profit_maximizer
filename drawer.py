import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly import tools
import numpy as np
from pandas import DataFrame
from streamlit import plotly_chart

def draw_sale_history(sale_history: DataFrame) -> None:
    max_range_y = np.ceil(max(sale_history["qty"]) * 1.15)
    fig = px.line(sale_history, x="date", y="qty", range_y=[0, max_range_y])
    plotly_chart(fig)

def draw_resell_listings(listings: DataFrame) -> None:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=listings["world"], y=listings["total"], name="Total", xaxis="x1", yaxis="y2", width=0.5),
        secondary_y=False,

    )

    fig.add_trace(
        go.Bar(x=listings["world"], y=listings["price_per_unit"], name="Price per Unit", xaxis="x2", yaxis="y2", width=0.5, offset=0.05),
        secondary_y=True
    )

    fig.update_layout(barmode="group", title_text="Lowest Listings per World", legend_title_text="Costs")

    fig.update_xaxes(title_text="World",)
    fig.update_yaxes(title_text="total", secondary_y=False)
    fig.update_yaxes(title_text="price per unit", secondary_y=True)
    plotly_chart(fig)