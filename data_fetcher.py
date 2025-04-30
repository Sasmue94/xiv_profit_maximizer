# this module is made to request data and handle the requested data in the needed manner

import pandas as pd
import json
import streamlit as st
import requests
import datetime
from pandas import DataFrame
from requests import Response

# creates a df containing all item names in en, de, fr, ja
@st.cache_data
def map_items(filename: str = "itemNames.json", lang: str = "de") -> pd.DataFrame:
    """
    Loads local json file and creates a df out of its contents \n
    :param filename: json file containing item names in different languages
    :param lang: specified language str to map itemnames
    :return items: Dataframe containing item IDs and corresponding item names
    in different languages
    """
    with open (filename, "r", encoding="utf-8") as file:
        items = json.load(file)
    items = DataFrame(items).transpose()
    marketable_items = get_marketable_items()
    empty_row = pd.DataFrame({"en": "", "de": "", "fr": "", "ja": ""}, index=[0])
    items = pd.concat([empty_row, items], ignore_index=True)
    items = items.iloc[marketable_items]
    items = items[items[lang] != ""]
    items.index.name = "item_id"
    items = items.reset_index(drop=False)
    return items

# convert response obj to readable dict
def convert_response(response: Response) -> dict:
    """
    converts an API response to dict \n
    :param response: Response to http request 
    :return Response Obj: dictionary containing response data 
    """
    if response.status_code == 200:
        data = response.json()
    else:
        data = {}
    return data

# request xivapi for item info
@st.cache_data
def get_item_info(item_id: int) -> dict[str:any]:
    """
    requests xivapi with the specified item_id \n
    :param item_id: a ff xiv item ID
    :return item Info: returns a Dataframe containing requested data
    """
    url = f"https://xivapi.com/item/{item_id}"
    return convert_response(requests.get(url))

# get ID corresponding to item name in given language
@st.cache_data
def get_item_id(items: pd.DataFrame, lang: str, selected_item: str) -> int:
    """
    searches item Dataframe for a specific item name \n
    in given language, returns corresponding id \n
    :param items: Pandas Dataframe containing item ids and item names per language
    :return Item ID: returns an int containing item ID of selected item
    """
    target_item_id = items[items[lang] == selected_item]["item_id"].iat[0]
    return target_item_id

# check if item is craftable
@st.cache_data
def isCraftable(item_data: dict) -> bool:
    """
    checks item data for recipe, if it contains recipes, \n
    the item is craftable \n
    :param item_data: dictionary containing data about item in question
    :return craftable: Returns bool containing information if item is craftable
    """
    return "Recipes" in item_data.keys()

# get job name to corresponding job id requesting xivapi
@st.cache_data
def get_job(job_id: int) -> str:
    """
    requests xivapi with the specified job_id \n
    :param job_id: a ff xiv job ID
    :return job name: returns a string containing the corresponding Job name
    """
    url = f"https://xivapi.com/ClassJob/{job_id}"
    return convert_response(requests.get(url))

# get rexipe contents of given recipe id from xivapi
@st.cache_data
def get_recipes(recipe_id: int) -> list[dict]:
    """
    requests xivapi with the specified recipe_id \n
    :param recipe_id: a ff xiv recipe ID
    :return recipe contents: returns a Dataframe containing recipe data
    """
    url = f"https://xivapi.com/recipe/{recipe_id}"
    return convert_response(requests.get(url))

# requests universalis, returns all marketable items in the game
@st.cache_data
def get_marketable_items() -> list[int]:
    """
    requests universalis for a list of marketable items \n
    :return marketable items: returns a Dataframe containing all marketable items
    """
    url = "https://universalis.app/api/v2/marketable"
    return convert_response(requests.get(url))

# requests universalis, returns recent sales of specified item on specified world
@st.cache_data
def get_sale_history(world: str, item_id: int) -> dict:
    """
    requests universalis with the specified item_id for corresponding listings \n
    on the market board on the given world \n
    :param item_id: a ff xiv item ID
    :param world: a ff xiv world / servername
    :return sale history: returns a Dataframe containing recent sales of the item
    """    
    url = f"https://universalis.app/api/v2/history/{world}/{item_id}?minSalePrice=0&maxSalePrice=2147483647"
    return convert_response(requests.get(url))

# reformats sale history to make it more usable
def harmonise_sale_history(sale_history: list[dict]) -> DataFrame:
    """
    takes sale history response and converts it into an easier to use data format \n
    :param sale_history: a list of ff xiv market board sales
    :return harmonised sales list: returns a Dataframe containing sales of an item
    """
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

# get listings of specified items (list) on all worlds of the given Dataceneter
def get_listings(item_ids: list[int], datacenter: str) -> dict[str:any]:
    """
    requests universalis with specified datacenter and item_ids \n
    :param item_ids: a list of ff xiv item IDs
    :return Listing data: returns a Dataframe containing all listings of item across specified Datacenter
    """
    id_str_list = []
    for id in item_ids:
        id_str_list.append(str(id))
    ids = str.join(",", id_str_list)
    url = f"https://universalis.app/api/v2/{datacenter}/{ids}"
    return convert_response(requests.get(url))

# check listings for specified amounts of needed items
def get_lowest_listings(listings: list[dict[str:any]], item_count: int) -> DataFrame:
    """
    searches provided listings for the cheapest listing >= needed item count \n
    :param listings: a list of ff xiv market board listings per item
    :param item_count: Number of needed items
    :return cheapest listings: returns a Dataframe containing the best suiting market board listings
    """
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

# check listings for specified amounts of needed items
# also diferentiates HQ and NQ Items
def get_cheapest_materials(listings: list[dict[str:any]], item_count: int) -> DataFrame:
    """
    searches provided listings for the cheapest listing >= needed item count \n
    takes hq and nq into account \n
    :param listings: a list of ff xiv market board listings per item
    :param item_count: Number of needed items
    :return cheapest listings: returns a Dataframe containing the best suiting market board listings
    """
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

# get recipe ingredients
def get_ingredients(recipe_data: dict) -> dict:
    """
    Check recipe data for item ids and the amount needed \n
    :param recipe_data: a dict containing ff xiv recipe information
    :return ingredients: returns a python dictionary containing item IDs and Number of items needed
    """
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
