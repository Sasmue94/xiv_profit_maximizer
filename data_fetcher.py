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

def get_first_listing(item_id: int, world: str, hq: bool, fallback_price: int) -> int:
    """
    requests universalis with specified world and item_id \n
    :param item_id: a ff xiv item IDs
    :return Listing data: returns either the first price listed or the fallback price
    """
    url = f"https://universalis.app/api/v2/{world}/{item_id}?entries=1&hq={hq}"
    val = convert_response(requests.get(url))["listings"]
    if val:
        price = val[0]["pricePerUnit"]
    else:
        price = fallback_price
    return price

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

# get recipe ingredients
def get_ingredients(recipe_data: dict, number_of_crafts: int) -> dict:
    """
    Check recipe data for item ids and the amount needed \n
    :param recipe_data: a dict containing ff xiv recipe information
    :return ingredients: returns a python dictionary containing item IDs and Number of items needed
    """
    ingredients = {}
    for i in range(0, 8):
        if recipe_data[f"AmountIngredient{i}"] > 0:
            ingredients[recipe_data[f"ItemIngredient{i}TargetID"]] = recipe_data[f"AmountIngredient{i}"] * number_of_crafts
    return ingredients

def get_lowest_sum(entries: list[dict], needed_items: int, buy_hq: bool = False) -> list[dict]:
    """
    Takes all Listings of an item and a target itemcount as input. Goes through all \n
    listings and looks for the cheapest combination reaching the desired itemcount. \n
    :param entries: Pandas Dataframe containing all entries regarding a specific item.
    :param needed_items: Int representing the number of desired items.
    :return best_combination: List containing the cheapest combination of entry dicts. 
    """

    if buy_hq:
        entries = pd.DataFrame(entries)
        entries = entries[entries["hq"] == buy_hq].copy()
        entries = entries.to_dict(orient="records")
    
    # To store the best combination of entries
    best_combination = []
    lowest_total = float('inf')
    best_quantity_sum = 0
    
    # Try all possible combinations of entries, starting from the first entry
    for i in range(len(entries)):
        current_combination = []
        current_total = 0
        current_quantity_sum = 0
        
        for j in range(i, len(entries)):
            current_combination.append(entries[j])
            current_quantity_sum += entries[j]["quantity"]
            current_total += entries[j]["total"]
            
            # Check if quantity is enough
            if current_quantity_sum >= needed_items:
                # check if combination has smaller total
                if current_total < lowest_total:
                    best_combination = current_combination.copy()
                    lowest_total = current_total
                    best_quantity_sum = current_quantity_sum
                break
    
    # if there are not enough listings, return entire list
    if best_quantity_sum < needed_items:
        return entries

    return best_combination

