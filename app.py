import streamlit as st
import pandas as pd
import data_fetcher as df

@st.cache_data
def get_item_id(items: pd.DataFrame, lang: str, selected_item: str) -> str:
    target_item_id = items[items[lang] == selected_item].index[0]
    return target_item_id

st.set_page_config(page_title="xiv profit maximizer", page_icon="💲", layout="wide", initial_sidebar_state="collapsed", menu_items=None)

languages = ["de", "en", "fr", "ja"]

dcs = {
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


left, right = st.columns([8, 2])
with left:
    st.header("XIV Profit Maximizer")
with right:
    lang = st.selectbox(label="Language", options=languages, key="language")


items = df.map_items(lang=lang)
l, r = st.columns(2)
with l:
    dc = st.selectbox(label="Datacenter", options=dcs.keys())
    item_filter = st.text_input(label="Filter items", value="")
    items = items[items[lang].str.contains(item_filter)]
    amount = st.number_input(label="No. of Items to craft", min_value=1, step=1)

with r:
    world = st.selectbox(label="Server", options=dcs[dc])
    selected_item = st.selectbox(label="select item", options=items[lang])
    sale_price = st.number_input(label="price to sell the item for", min_value=1, step=1)

lookup = st.button(label="Lookup")

if lookup:
    target_item_id = get_item_id(items=items, lang=lang, selected_item=selected_item)
    st.write(target_item_id)
    st.write(df.get_listings(item_ids=["30757"], datacenter="Light"))

        

