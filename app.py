import streamlit as st
import pandas as pd
import numpy as np
import data_fetcher as df
import drawer as dr
from language_map import language_map

st.set_page_config(page_title="XIV Profit Maximizer", page_icon="💲", layout="wide", initial_sidebar_state="collapsed", menu_items=None)

#marketable_items = df.get_marketable_items()

languages = ["de", "en", "fr", "ja"]

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

gapL, left, right, gapR = st.columns([1, 8, 2, 1], gap = "large")
with left:
    st.header("XIV Profit Maximizer")
with right:
    st.write("")
    lang = st.selectbox(label="Language", options=languages, key="language")
    items = df.map_items(lang=lang)

gapL, l, r, gapR = st.columns([1,5,5,1], gap="large")
with l:
    dc = st.selectbox(label=language_map["dc"][lang], options=dcs.keys())
    item_filter = st.text_input(label=language_map["filter"][lang], value="")
    filtered_items = items[items[lang].str.lower().str.contains(item_filter.lower())]
    amount = st.number_input(label=language_map["count"][lang], min_value=1, step=1)

with r:
    world = st.selectbox(label=language_map["world"][lang], options=dcs[dc])
    selected_item = st.selectbox(label=language_map["item_select"][lang], options=filtered_items[lang])
    #sale_price = st.number_input(label="price to sell the item for", min_value=1, step=1)

gapL, button_area, gapR = st.columns([10, 1, 1], gap="large")
search = button_area.button(label=language_map["search"][lang], use_container_width=True)

gapL, m, gapR = st.columns([1,10,1], gap="large")
if search:
    target_item_id = df.get_item_id(items=items, lang=lang, selected_item=selected_item)
    hist = df.get_sale_history(world=world, item_id=target_item_id)
    hist = df.harmonise_sale_history(sale_history=hist)
    hist_agg = hist.groupby("date").agg(sum).reset_index()
    with m:
        st.subheader(f"{language_map['history'][lang]}: {selected_item}")
        dr.draw_sale_history(sale_history=hist_agg)
        item_data = df.get_item_info(item_id=target_item_id)
        if df.isCraftable(item_data=item_data):
            recipes = item_data["Recipes"]
            for recipe in recipes:
                recipe_id = recipe["ID"]
                job = recipe["ClassJobID"]
                job_data = df.get_job(job)
                job_name = job_data[f"Name_{lang}"]
                job_recipe = df.get_recipes(recipe_id=recipe_id)
                ingredients = df.get_ingredients(job_recipe)
                recipe_listings = df.get_listings(list(ingredients.keys()), datacenter=dc)
                for i in recipe_listings["items"]:
                    st.subheader(items[items["item_id"] == int(i)][lang].iat[0])
                    lowest_listings = df.get_lowest_listings(listings=recipe_listings["items"][i]["listings"], item_count=ingredients[int(i)])
                    dr.draw_resell_listings(listings=lowest_listings, 
                                    world_label=language_map["world"][lang], 
                                    total_label=language_map["total"][lang], 
                                    unit_label=language_map["unit"][lang],
                                    title_label=language_map["listing_bar"][lang])

        else:
            st.subheader(f"{language_map['resell'][lang]}")
            listings = df.get_listings(item_ids=[target_item_id], datacenter=dc)["listings"]
            lowest_listings = df.get_lowest_listings(listings=listings, item_count=amount)
            dr.draw_resell_listings(listings=lowest_listings, 
                                    world_label=language_map["world"][lang], 
                                    total_label=language_map["total"][lang], 
                                    unit_label=language_map["unit"][lang],
                                    title_label=language_map["listing_bar"][lang])

        

