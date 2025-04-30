import pandas as pd
import json
import streamlit as st
import requests
import datetime
from pandas import DataFrame
from requests import Response

@st.cache_data
def map_items(filename: str = "itemNames.json", lang: str = "de") -> pd.DataFrame:
    with open (filename, "r", encoding="utf-8") as file:
        items = json.load(file)
    items = DataFrame(items).transpose()
    marketable_items = get_marketable_items()
    empty_row = pd.DataFrame({"en": "", "de": "", "fr": "", "ja": ""}, index=[0])
    items = pd.concat([empty_row, items], ignore_index=True)
    items = items.iloc[marketable_items]
    items = items[items[lang] != ""]
    items.index.name = "item_id"
    return items

def convert_response(response: Response) -> dict:
    if response.status_code == 200:
        data = response.json()
    else:
        data = {}
    return data

@st.cache_data
def get_item_info(item_id: int) -> dict[str:any]:
    url = f"https://xivapi.com/item/{item_id}"
    return convert_response(requests.get(url))

@st.cache_data
def get_item_id(items: pd.DataFrame, lang: str, selected_item: str) -> int:
    target_item_id = items[items[lang] == selected_item].index[0]
    return target_item_id

@st.cache_data
def isCraftable(item_data: dict) -> bool:
    return "Recipes" in item_data.keys()

@st.cache_data
def get_job(job_id: int) -> str:
    url = f"https://xivapi.com/ClassJob/{job_id}"
    return convert_response(requests.get(url))

@st.cache_data
def get_recipes(recipe_id: int) -> list[dict]:
    url = f"https://xivapi.com/recipe/{recipe_id}"
    return convert_response(requests.get(url))

@st.cache_data
def get_marketable_items() -> list[int]:
    url = "https://universalis.app/api/v2/marketable"
    return convert_response(requests.get(url))

@st.cache_data
def get_sale_history(world: str, item_id: int) -> dict:
    url = f"https://universalis.app/api/v2/history/{world}/{item_id}?minSalePrice=0&maxSalePrice=2147483647"
    return convert_response(requests.get(url))

def harmonise_sale_history(sale_history: list[dict]) -> DataFrame:
    value_dict: dict[str:list] = {
        "date" : [],
        "qty" : [],
        "ppu" : []
    }
    if "entries" in sale_history:
        for entry in sale_history["entries"]:
            value_dict["date"].append(datetime.datetime.fromtimestamp(entry["timestamp"]).date())
            value_dict["qty"].append(entry["quantity"])
            value_dict["ppu"].append(entry["pricePerUnit"])
    return pd.DataFrame(value_dict)
    
def get_listings(item_ids: list[int], datacenter: str) -> dict[str:any]:
    id_str_list = []
    for id in item_ids:
        id_str_list.append(str(id))
    ids = str.join(",", id_str_list)
    url = f"https://universalis.app/api/v2/{datacenter}/{ids}"
    return convert_response(requests.get(url))

def get_lowest_listings(listings: list[dict[str:any]], item_count: int) -> dict:
    lowest_listings: dict = {}
    if listings:
        for entry in listings:
            qty: int = entry["quantity"]
            total: int = entry["total"]
            world: str = entry["worldName"]
            ppu: int = entry["pricePerUnit"]
            if world not in lowest_listings:
                lowest_listings[world] = {"quantity": qty, "total": total, "price_per_unit": ppu}
            elif qty >= item_count and total < lowest_listings[world]["total"]:
                lowest_listings[world] = {"quantity": qty, "total": total, "price_per_unit": ppu}
    df = pd.DataFrame(lowest_listings).transpose()
    df.index.name = "world"
    df = df.reset_index(drop=False)                
    return df

def get_cheapest_materials(listings: list[dict[str:any]], item_count: int) -> dict:
    lowest_listings: dict = {}
    if listings:
        for entry in listings:
            hq: bool = entry["hq"]
            qty: int = entry["quantity"]
            total: int = entry["total"]
            ppu: int = entry["pricePerUnit"]
            world: str = entry["worldName"]
            if world not in lowest_listings:
                if hq:
                    lowest_listings[world] = {
                        "hq" : {"quantity": qty, "total": total, "price_per_unit": ppu} 
                    }
                else:
                    lowest_listings[world] = {
                        "nq" : {"quantity": qty, "total": total, "price_per_unit": ppu} 
                    }
            else:
                if hq and "hq" not in lowest_listings[world]:
                    lowest_listings[world]["hq"] = {"quantity": qty, "total": total} 

                elif not hq and "nq" not in lowest_listings[world]:
                    lowest_listings[world]["nq"] = {"quantity": qty, "total": total} 

                elif hq and qty >= item_count and total < lowest_listings[world]["hq"]["total"]:
                    lowest_listings[world]["hq"] = {"quantity": qty, "total": total}

                elif not hq and qty >= item_count and total < lowest_listings[world]["nq"]["total"]:
                    lowest_listings[world]["nq"] = {"quantity": qty, "total": total}
    return pd.DataFrame(lowest_listings)

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
        if isCraftable(item_data=item_data):
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
