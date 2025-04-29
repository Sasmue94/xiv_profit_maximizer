import pandas as pd
import json
import streamlit as st
import requests
from pandas import DataFrame
from requests import Response

def map_items(filename: str = "itemNames.json", lang: str = "de") -> pd.DataFrame:
    with open (filename, "r", encoding="utf-8") as file:
        items = json.load(file)
    items = DataFrame(items).transpose()
    items = items[items[lang] != ""]
    return items

@st.cache_data
def get_item_info(item_id: str) -> Response:
    url = f"https://xivapi.com/item/{item_id}"
    return requests.get(url)

@st.cache_data
def get_job(job_id: str) -> Response:
    url = f"https://xivapi.com/ClassJob/{job_id}"
    return requests.get(url)

@st.cache_data
def get_recipes(recipe_id: str) -> Response:
    url = f"https://xivapi.com/recipe/{recipe_id}"
    return requests.get(url)

@st.cache_data
def get_listings(item_ids: list[str], datacenter: str) -> Response:
    ids = str.join(",", item_ids)
    url = f"https://universalis.app/api/v2/{datacenter}/{ids}"
    return url

def convert_response(response: Response) -> dict:
    if response.status_code == 200:
        data = response.json()
    else:
        data = {}
    return data

def get_ingredients(recipe_data: dict) -> dict:
    ingredients = {}
    for i in range(0, 8):
        if recipe_data[f"AmountIngredient{i}"] > 0:
            ingredients[recipe_data[f"ItemIngredient{i}TargetID"]] = recipe_data[f"AmountIngredient{i}"]
    return ingredients

if __name__ == "__main__":

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

    lang: str = "de"
    item_id: str = "30757"
    items: DataFrame = map_items()
    item_response: Response = get_item_info(item_id=item_id)

    print(items.loc[item_id][lang])

    item_data: dict = convert_response(response=item_response)
    if item_data:
        name: str = item_data[f"Name_{lang}"]
        print(name)
        recipes: list = item_data["Recipes"] 
        for r in recipes:
            job_response: Response = get_job(r["ClassJobID"])
            job_data: dict = convert_response(response=job_response)
            if job_data:
                job_name: str = job_data[f"Name_{lang}"]
                print(job_name)
            recipe_response: Response = get_recipes(recipe_id=r["ID"])
            recipe_data: dict = convert_response(response=recipe_response)
            if recipe_data:
                ingredients: dict = get_ingredients(recipe_data=recipe_data)
                for id in ingredients:
                    print(ingredients[id], items[f"{id}"][lang])
            else:
                print("not craftable")
