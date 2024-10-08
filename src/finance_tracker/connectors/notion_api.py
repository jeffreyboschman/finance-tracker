"""Getting data from Notion API"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")


def get_database(database_id: str, num_pages: int | None = None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """

    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    data = response.json()

    # json_data = json.dumps(data, indent=4)
    # print(json_data)

    database_pages = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        data = response.json()
        database_pages.extend(data["results"])

    return database_pages
