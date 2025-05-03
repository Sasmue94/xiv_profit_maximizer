# main page of the app

import streamlit as st
import data_fetcher as df
import drawer as dr
import threading
import pandas as pd
from language_map import language_map
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# configure layout
st.set_page_config(page_title="XIV Profit Maximizer", page_icon="💲", layout="wide", initial_sidebar_state="collapsed", menu_items=None)

shoppinglist: dict = {}

# group desired listings by world to create a shoppinglist
def shop_data(listings: pd.DataFrame, items_needed: int, item_name: str, ingredient_data: dict, buy_hq: bool = False) -> None:
    if not df.isCraftable(item_data=ingredient_data):
        buy_hq = False
    listings_to_buy = df.get_lowest_sum(entries=listings, needed_items=items_needed, buy_hq=buy_hq)
    for entry in listings_to_buy:
        if buy_hq:
            entry["name"] = f"{item_name} (HQ)"
        else:    
            entry["name"] = item_name
        if entry:
            world = entry["worldName"]
            shoppinglist[world].append(entry)

# convert shoppinglist into a pandas Dataframe
def convert_shoppinglist(shoppinglist: dict) -> pd.DataFrame:
    harmonised = {
        "World":[],
        "Retainer":[],
        "Item":[],
        "Quantity":[],
        "Price_per_Unit":[],
        "Total":[]
    }
    for world in shoppinglist:
        for entry in shoppinglist[world]:
            harmonised["World"].append(entry["worldName"])
            harmonised["Retainer"].append(entry["retainerName"])
            harmonised["Item"].append(entry["name"])
            harmonised["Quantity"].append(entry["quantity"])
            harmonised["Price_per_Unit"].append(entry["pricePerUnit"])
            harmonised["Total"].append(entry["total"])
    return pd.DataFrame(harmonised)

# All possible languages given itemNames.json
languages: list[str] = ["de", "en", "fr", "ja"]

# relevant Datacenters as of 04/25
dcs: dict[str:list[str]] = {
    "Aether":["Adamantoise","Cactuar","Faerie","Gilgamesh","Jenova","Midgardsormr","Sargatanas","Siren"],
    "Chaos":["Cerberus","Louisoix","Moogle","Omega","Phantom","Ragnarok","Sagittarius","Spriggan"],
    "Crystal":["Balmung","Brynhildr","Coeurl","Diabolos","Goblin","Malboro","Mateus","Zalera"],
    "Dynamis":["Halicarnassus","Maduin","Marilith","Seraph"],
    "Elemental":["Aegis","Atomos","Carbuncle","Garuda","Gungnir","Kujata","Tonberry","Typhon"],
    "Gaia":["Alexander","Bahamut","Durandal","Fenrir","Ifrit","Ridill","Tiamat","Ultima"],
    "Light":["Alpha","Lich","Odin","Phoenix","Raiden","Shiva","Twintania","Zodiark"],
    "Mana":["Anima","Asura","Chocobo","Hades","Ixion","Masamune","Pandaemonium","Titan"],
    "Materia":["Bismarck","Ravana","Sephirot","Sophia","Zurvan"],
    "Meteor":["Belias","Mandragora","Ramuh","Shinryu","Unicorn","Valefor","Yojimbo","Zeromus"],
    "Primal":["Behemoth","Excalibur","Exodus","Famfrit","Hyperion","Lamia","Leviathan","Ultros"]
}

# render gaps for visual purposes
gapL, left, right, gapR = st.columns([1, 8, 2, 1], gap = "large")
with left:
    st.header("XIV Profit Maximizer")
with right:
    st.write("")
    # select language
    lang = st.selectbox(label="Language", options=languages, key="language")

items = df.map_items(lang=lang)

# form on top part of page
gapL, l, r, gapR = st.columns([1,5,5,1], gap="large")
with l:
    dc = st.selectbox(label=language_map["dc"][lang], options=dcs.keys())
    item_filter = st.text_input(label=language_map["filter"][lang], value="")
    filtered_items = items[items[lang].str.lower().str.contains(item_filter.lower())]
    crafts = st.number_input(label=language_map["count"][lang], min_value=1, step=1)

with r:
    world = st.selectbox(label=language_map["world"][lang], options=dcs[dc])
    selected_item = st.selectbox(label=language_map["item_select"][lang], options=filtered_items[lang])
    fallback_price = st.number_input("Price if no listing is active", min_value=1, step=1)
    buy, craft = st.columns(2)
    buy_hq = buy.checkbox(label = "Buy HQ")
    craft_hq = craft.checkbox(label = "Craft HQ")

for server in dcs[dc]:
    shoppinglist[server] = []

# align search button to right end of form 
gapL, button_area, gapR = st.columns([10, 1, 1], gap="large")
search = button_area.button(label=language_map["search"][lang], use_container_width=True)
gapL, m, gapR = st.columns([1,10,1], gap="large")

# when search is initialized
if search:

    # get item info
    target_item_id = df.get_item_id(items=items, lang=lang, selected_item=selected_item)
    hist = df.get_sale_history(world=world, item_id=target_item_id)
    hist = df.harmonise_sale_history(sale_history=hist)
    hist_agg = hist.groupby("date").agg(sum).reset_index()
    with m:

        # display sale history
        lowest_price = df.get_first_listing(item_id=target_item_id, world=world, hq=craft_hq, fallback_price=fallback_price)
        st.subheader(f"{language_map['history'][lang]}: {selected_item}")
        st.subheader(f"Current Price on {world}: {lowest_price} Gil")
        dr.draw_sale_history(sale_history_agg=hist_agg, sale_history=hist)
        item_data = df.get_item_info(item_id=target_item_id)

        # item is craftable
        amount_result = 0
        if df.isCraftable(item_data=item_data):
            recipes = item_data["Recipes"]
            for recipe in recipes:
                recipe_id = recipe["ID"]
                job = recipe["ClassJobID"]
                job_data = df.get_job(job)
                job_name = job_data[f"Name_{lang}"]
                job_recipe = df.get_recipes(recipe_id=recipe_id)
                amount_result = job_recipe["AmountResult"]
                ingredients = df.get_ingredients(recipe_data=job_recipe, number_of_crafts=crafts)
                recipe_listings = df.get_listings(list(ingredients.keys()), datacenter=dc)

                # get prices for every ingredient in the recipe
                threads = []
                for i in recipe_listings["items"]: # there is a maximum of 7 ingredients per craft
                    # show best possible purchases on each world
                    lowest_listings = df.get_lowest_listings(listings=recipe_listings["items"][i]["listings"], item_count=ingredients[int(i)])
                    thread = threading.Thread(target=dr.draw_lowest_listings, args=[i, items, lang, language_map, lowest_listings]) # <= 7 Threads
                    add_script_run_ctx(thread, get_script_run_ctx())
                    threads.append(thread)
                    thread.start()

                for thread in threads:
                    thread.join()

                for i_id in recipe_listings["items"]:
                    item_name = items[items["item_id"] == int(i_id)][lang].iat[0]
                    ingredient_data = df.get_item_info(int(i_id))
                    shop_data(listings=recipe_listings["items"][i_id]["listings"], ingredient_data=ingredient_data, items_needed=ingredients[int(i_id)], item_name=item_name, buy_hq=buy_hq)

            shoppinglist = convert_shoppinglist(shoppinglist)
            st.subheader("Shoppinglist:")
            st.dataframe(shoppinglist, hide_index=True)
            total_cost = sum(shoppinglist["Total"])
            max_turnover = crafts * amount_result * lowest_price
            profit = max_turnover - total_cost
            st.subheader(f"Turnover: {max_turnover} Gil, Total Cost: {total_cost} Gil -> estimated Profit: {profit} Gil")
            calculations = pd.DataFrame({"Turnover": max_turnover, "Total Cost": total_cost, "Win/Loss": profit}, index=["Gil"]).transpose()
            calculations.index.name = "Cost / Income"
            st.subheader("Win / Loss Visualization")    
            dr.draw_profit_bars(calculations=calculations)
            st.subheader("Cost Spread:")
            dr.draw_cost_spread_pie(shoppinglist=shoppinglist)

        # item is not craftable
        else:
            st.subheader(f"{language_map['resell'][lang]}")
            # get all listings of said item
            listings = df.get_listings(item_ids=[target_item_id], datacenter=dc)["listings"]
            lowest_listings = df.get_lowest_listings(listings=listings, item_count=crafts)
            # show cheapest listings across different worlds for possible buying / reselling
            shop_data(listings=listings, items_needed=crafts, item_name=selected_item, ingredient_data=item_data)
            shoppinglist = convert_shoppinglist(shoppinglist=shoppinglist)
            st.dataframe(data=shoppinglist, hide_index=True)
            dr.draw_resell_listings(listings=lowest_listings, 
                                    world_label=language_map["world"][lang], 
                                    total_label=language_map["total"][lang], 
                                    unit_label=language_map["unit"][lang],
                                    title_label=language_map["listing_bar"][lang],
                                    amount_label=language_map["amount"][lang])

        

