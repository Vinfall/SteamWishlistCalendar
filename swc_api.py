import argparse

# import dateparser
import requests

# import json
# import re


# import time
# from datetime import datetime, timedelta, timezone
# from pathlib import Path


# from ics import Calendar, Event

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--id", type=str, required=True)

# init
wishlist_data = []


def get_wishlist(steamid):
    url = f"https://api.steampowered.com/IWishlistService/GetWishlist/v1/?steamid={steamid}"

    response = requests.get(url, timeout=10)

    # in case of broken Steam API
    if response.status_code == 200:
        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            exit()

    # store appid as int
    if "response" in response_data and "items" in response_data["response"]:
        for item in response_data["response"]["items"]:
            if "appid" in item:
                # init dict
                wishlist_item = {
                    "appid": int(item["appid"]),
                    "name": "",
                    "released": "",
                    "description": "",
                }
                wishlist_data.append(wishlist_item)

    return wishlist_data


def get_name(wishlist_with_appid):
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        response_data = response.json()
        app_list = response_data["applist"]["apps"]

        # map name in wishlist with appid
        app_dict = {app["appid"]: app["name"] for app in app_list}

        for item in wishlist_with_appid:
            if item["appid"] in app_dict:
                item["name"] = app_dict[item["appid"]]

    return wishlist_with_appid


def get_detail(wishlist_with_name):
    count = 0
    for item in wishlist_with_name:
        # only loop five times to avoid rate limit
        count += 1
        if count == 3:
            break
        else:
            # still int
            appid = item["appid"]
            url = f"https://store.steampowered.com/api/appdetails?appids={appid}"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                response_data = response.json()
                app_data = response_data.get(str(appid), {}).get("data", {})

                # update keys
                item["name"] = app_data.get("name", item["name"])
                item["released"] = app_data.get("release_date", {}).get(
                    "date", item["released"]
                )
                item["description"] = app_data.get("short_description", "")

    return wishlist_with_name


# def make_calendar(wishlist_full):


steamid = ""
wishlist = get_wishlist(steamid)
# wishlist = get_name(wishlist)
wishlist_full = get_detail(wishlist)


print(wishlist_full)
# unicode_escape?
# print(json.dumps(wishlist, indent=4))
