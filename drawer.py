# this module is made for drawing any needed visualisations of data on screen

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from pandas import DataFrame
from streamlit import plotly_chart

# draw line graph of sales history on screen
def draw_sale_history(sale_history_agg: DataFrame, sale_history: DataFrame) -> None:
    """
    draws line chart of requested sale history of item on current world \n
    :param sale_history: DataFrame containing the last saved sales history of an items
    :return: None
    """
    if not sale_history_agg.empty:
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=sale_history_agg["date"], y=sale_history_agg["qty"], name="Total Amount Sold"),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(x=sale_history["date"], y=sale_history["ppu"], name="Price Per Unit", mode="markers"),
            secondary_y=True
        )

        fig.update_layout(legend_title_text="Historic Sales", xaxis_title="Date")

        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Total Amount sold", secondary_y=False)
        fig.update_yaxes(title_text="Price per unit", secondary_y=True)
        
        plotly_chart(fig)
    else:
        st.subheader("No current sales")

# draw bar chart of the most fitting, cheapes listings of an item across all worlds of a given Datacenter
def draw_resell_listings(listings: DataFrame, world_label: str, total_label: str, unit_label: str, title_label: str, amount_label: str) -> None:
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

    fig.add_trace(
        go.Bar(x=listings["world"], y=listings["quantity"], width=0, name=amount_label)
    )

    fig.update_layout(title_text=title_label, legend_title_text="Costs", xaxis_title=world_label, hovermode="x unified")

    fig.update_xaxes(title_text=world_label)
    fig.update_yaxes(title_text=total_label, secondary_y=False)
    fig.update_yaxes(title_text=unit_label, secondary_y=True)
    plotly_chart(fig)

# draw bar chart of expected crafting cost, turnover and estimated profit
def draw_profit_bars(calculations: DataFrame) -> None:
    """
    draws bar chart of expected crafting cost, turnover and estimated profit \n
    :param calculations: DataFrame containing current item crafting cost, expected turnover and estimated profit
    :return: None
    """
    fig = px.bar(calculations)
    plotly_chart(fig)

# draw pie chart showing which item has what share of the cost
def draw_cost_spread_pie(shoppinglist: DataFrame) -> None:
    """
    draws pie chart showing which item has what share of the cost \n
    :param calculations: DataFrame containing current shoppinglist
    :return: None
    """
    fig = px.pie(data_frame=shoppinglist, values="Total", names = "Item")
    plotly_chart(fig)

# draw bar chart of cheapest listings meeting the required item number per world
def draw_lowest_listings(item: str, items: DataFrame, lang: str, language_map: dict[str:dict], lowest_listings: DataFrame) -> None:
    """
    draws bar chart of cheapest listings meeting the required item count in quantity \n
    draws 2 bars with 2 y-axes, total price and price per unit \n
    :param item: name of an item as str
    :param items: Dataframe containing item information
    :param lang: string specifieng output language
    :language map: dict containing language mapping
    :param lowest_listings: Dataframe containing the lowest listings of an item
    :return: None
    """
    gapL, m, gapR = st.columns([1,10,1], gap="large")
    with m:
        st.subheader(items[items["item_id"] == int(item)][lang].iat[0])
        # show best possible purchases on each world
        draw_resell_listings(listings=lowest_listings, 
                        world_label=language_map["world"][lang], 
                        total_label=language_map["total"][lang], 
                        unit_label=language_map["unit"][lang],
                        title_label=language_map["listing_bar"][lang],
                        amount_label=language_map["amount"][lang])