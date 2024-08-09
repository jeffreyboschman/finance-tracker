import requests
import json
from datetime import datetime, timezone
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('DATABASE_ID')




def extract_select_type_info(props: dict, column_name: str) -> str | None:
    """
    Extracts the selected option's name from a Notion database row JSON
    based on the specified column name.

    Args:
        props (dict): A dictionary representing properties of a Notion
            database row. It is expected to have a key corresponding to
            the specified column_name, which contains a dictionary with
            a "select" key representing the information for a Select type option.
        column_name (str): The name of a Select type column from which to extract
            the selected option name.

    Returns:
        str: The name of the selected option in the specified Select type column.
            If the selected option information is found, its name is
            returned. If the column does not exist or if the "select"
            key is null, None is returned.
    """
    select_dict = props.get(column_name, {}).get("select", None)
    if select_dict is not None:
        selected_option = select_dict.get("name", None)
    else:
        # Handle the case when "select" is null
        selected_option = None

    return selected_option

def extract_rollup_type_info(props: dict, column_name: str) -> str | None:
    """
    Extracts the rollup information from a Notion database row dictionary
    based on the specified column name.

    Args:
        props (dict): A dictionary representing properties of a Notion
            database row. It is expected to have keys corresponding to
            different columns, each of which contains a dictionary with
            information about the column.
        column_name (str): The name of the column from which to extract
            the rollup information.

    Returns:
        list: The list of rollup values for the specified column. If the
            column does not exist or if it is not of type 'rollup', an
            empty list is returned.
    """
    rollup_info = []

    if column_name in props and props[column_name]["type"] == "rollup":
        rollup_data = props[column_name].get("rollup", {}).get("array", [])
        for item in rollup_data:
            if item["type"] == "relation":
                relation_data = item.get("relation", [])
                for relation_item in relation_data:
                    rollup_info.append(relation_item.get("id"))

    return rollup_info

def extract_number_type_info(props: dict, column_name: str) -> str | None:
    """
    Extracts the number value from a Notion database row JSON
    based on the specified column name.

    Args:
        props (dict): A dictionary representing properties of a Notion
            database row. It is expected to have a key corresponding to
            the specified column_name, which contains a dictionary with
            a "number" key representing the information for a Number type column.

    Returns:
        str: The number value for the row. If the number information is not found, None is returned.
    """
    number_value = props.get(column_name, {}).get("number", None)
    return number_value

def get_pages(num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    
    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    # json_data = json.dumps(data, indent=4)
    # print(json_data)

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results