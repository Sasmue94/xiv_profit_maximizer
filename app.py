import streamlit as st
import pandas as pd
import numpy as np
import data_fetcher as df
import drawer as dr

st.set_page_config(page_title="XIV Profit Maximizer", page_icon="💲", layout="wide", initial_sidebar_state="collapsed", menu_items=None)

#marketable_items = df.get_marketable_items()

languages = ["de", "en", "fr", "ja"]

language_map: dict[str:dict[str:str]] = {
    "dc" : {
        "en":"Datacenter",
        "de":"Datenzentrum",
        "fr":"Centre de données",
        "ja":"データセンター"
    },
    "world" : {
        "en" : "world",
        "de" : "Welt",
        "fr" : "Monde",
        "ja" : "世界"
    },
    "item_select" : {
        "en" : "select item",
        "de" : "Item auswählen",
        "fr" : "sélectionner item",
        "ja" : "項目を選択"
    },
    "filter" : {
        "en" : "filter items",
        "de" : "Items filtern",
        "fr" : "filtre item",
        "ja" : "フィルター 「アイテム」"
    },
    "count" : {
        "en" : "item count",
        "de" : "Anzahl herzustellender Items",
        "fr" : "Nombre d'items à fabriquer",
        "ja" : "クラフトアイテムの数"
    },
    "search" : {
        "en" : "search",
        "de" : "suchen",
        "fr" : "rechercher",
        "ja" : "探索"
    },
    "history": {
        "en" : "Sale History",
        "de" : "Verkaufshistorie",
        "fr" : "Historique des ventes",
        "ja" : "販売履歴"
    },
    "resell" : {
        "en" : "Not a craftable item, info for possible reselling:",
        "de" : "Kann nicht hergestellt werden, Preisinformationen für möglichen Wiederverkauf:",
        "fr" : "Ne peut être fabriqué, informations sur les prix pour une éventuelle revente:",
        "ja" : "製造不可、転売目的の価格情報："
    }

}

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
    lang = st.selectbox(label="Language", options=languages, key="language")
    items = df.map_items(lang=lang)

gapL, l, r, gapR = st.columns([1,5,5,1], gap="large")
with l:
    dc = st.selectbox(label=language_map["dc"][lang], options=dcs.keys())
    item_filter = st.text_input(label=language_map["filter"][lang], value="")
    items = items[items[lang].str.contains(item_filter)]
    amount = st.number_input(label=language_map["count"][lang], min_value=1, step=1)

with r:
    world = st.selectbox(label=language_map["world"][lang], options=dcs[dc])
    selected_item = st.selectbox(label=language_map["item_select"][lang], options=items[lang])
    #sale_price = st.number_input(label="price to sell the item for", min_value=1, step=1)

gapL, button_area, gapR = st.columns([10, 1, 1], gap="large")
lookup = button_area.button(label=language_map["search"][lang], use_container_width=True)

gapL, m, gapR = st.columns([1,10,1], gap="large")
if lookup:
    target_item_id = df.get_item_id(items=items, lang=lang, selected_item=selected_item)
    hist = df.get_sale_history(world=world, item_id=target_item_id)
    hist = df.harmonise_sale_history(sale_history=hist)
    hist_agg = hist.groupby("date").agg(sum).reset_index()
    with m:
        st.subheader(f"{language_map['history'][lang]}: {selected_item}")
        dr.draw_sale_history(sale_history=hist_agg)
        item_data = df.get_item_info(item_id=target_item_id)
        if df.isCraftable(item_data=item_data):
            pass
        else:
            st.subheader(f"{language_map['resell'][lang]}")
            listings = df.get_listings(item_ids=[target_item_id], datacenter=dc)["listings"]
            # st.write(listings)
            lowest_listings = df.get_lowest_listings(listings=listings, item_count=amount)
            # lowest_listings
            dr.draw_resell_listings(listings=lowest_listings)
            st.write(f"Estimated Profit: Price on {world}: {lowest_listings[lowest_listings['world'] == world]['total'].iat[0]} - {min(lowest_listings['total'])} = {lowest_listings[lowest_listings['world'] == world]['total'].iat[0] - min(lowest_listings['total'])}")

        

