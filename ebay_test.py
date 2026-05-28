import requests
from dotenv import load_dotenv
import os
import json
from tag_system import get_tags

load_dotenv()

APP_ID = os.getenv("EBAY_APP_ID")
CERT_ID = os.getenv("EBAY_CERT_ID")

def get_usd_to_jpy():
    try:
        response = requests.get("https://api.frankfurter.app/latest?from=USD&to=JPY", timeout=10)
        rate = response.json()["rates"]["JPY"]
        print(f"為替レート取得: 1USD = {rate}円")
        return round(rate)
    except Exception as e:
        print(f"為替レート取得失敗: {e} → デフォルト150円を使用")
        return 150

def get_access_token():
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }
    response = requests.post(url, headers=headers, data=data, auth=(APP_ID, CERT_ID))
    token = response.json()["access_token"]
    return token

def get_auction_cards():
    token = get_access_token()
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {"Authorization": f"Bearer {token}"}
    
    all_cards = []
    offset = 0
    limit = 200
    target =2000

    while len(all_cards) < target:
        params = {
            "q": "pokemon card PSA japanese",
            "limit": limit,
            "offset": offset,
            "filter": "buyingOptions:{AUCTION|BEST_OFFER}",
            "sort": "endingSoonest",
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        items = data.get("itemSummaries", [])
        total = data.get("total", 0)

        if not items:
            break

        for item in items:
            title = item["title"]
            if "price" not in item:
                continue
            if "PSA" not in title.upper():
                continue
            all_cards.append({
                "title": title,
                "price": item["price"]["value"],
                "currency": item["price"]["currency"],
                "image": item.get("image", {}).get("imageUrl", ""),
                "url": item["itemWebUrl"],
                "tags": get_tags(title),
                "date": item.get("itemCreationDate", ""),
                "buying_option": "AUCTION",
                "end_time": item.get("itemEndDate", ""),
            })

        offset += limit
        print(f"取得中... {len(all_cards)}件 / 総数{total}件")

        if offset >= total:
            break

    return all_cards

def get_fixed_price_cards():
    token = get_access_token()
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {"Authorization": f"Bearer {token}"}

    all_cards = []
    offset = 0
    limit = 200
    target = 3000

    while len(all_cards) < target:
        params = {
            "q": "pokemon card PSA japanese",
            "limit": limit,
            "offset": offset,
            "filter": "buyingOptions:{FIXED_PRICE},itemStartDate:[2026-05-16T00:00:00Z]",
            "sort": "newlyListed",
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        items = data.get("itemSummaries", [])
        total = data.get("total", 0)

        if not items:
            break

        for item in items:
            title = item["title"]
            if "price" not in item:
                continue
            if "PSA" not in title.upper():
                continue
            all_cards.append({
                "title": title,
                "price": item["price"]["value"],
                "currency": item["price"]["currency"],
                "image": item.get("image", {}).get("imageUrl", ""),
                "url": item["itemWebUrl"],
                "tags": get_tags(title),
                "date": item.get("itemCreationDate", ""),
                "buying_option": "FIXED_PRICE",
                "end_time": "",
            })

        offset += limit
        print(f"取得中... {len(all_cards)}件 / 総数{total}件")

        if offset >= total:
            break

    return all_cards

print("=== 為替レート取得 ===")
usd_to_jpy = get_usd_to_jpy()

print("=== オークション取得 ===")
auction_cards = get_auction_cards()
print(f"オークション：{len(auction_cards)}件")

print("=== 定価即決取得 ===")
fixed_cards = get_fixed_price_cards()
print(f"定価即決：{len(fixed_cards)}件")

all_cards = auction_cards + fixed_cards

with open("pokemon_data.json", "w", encoding="utf-8") as f:
    json.dump(all_cards, f, ensure_ascii=False, indent=2)

import datetime
rate_data = {
    "usd_to_jpy": usd_to_jpy,
    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
}
with open("rate.json", "w", encoding="utf-8") as f:
    json.dump(rate_data, f, ensure_ascii=False, indent=2)

print(f"合計：{len(all_cards)}件保存しました！")
print(f"為替レート保存：1USD = {usd_to_jpy}円")
