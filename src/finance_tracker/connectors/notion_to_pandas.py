"""For converting data from Notion API into Pandas DataFrames"""

import logging
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from finance_tracker.connectors import notion_utils
from finance_tracker.connectors.notion_api import get_database
from finance_tracker.utils.utils import timing_decorator

FINANCE_TRACKER_DATABASE_ID = os.getenv("FINANCE_TRACKER_DATABASE_ID")
SUB_CATEGORIES_DATABASE_ID = os.getenv("SUB_CATEGORIES_DATABASE_ID")
MAIN_CATEGORIES_DATABASE_ID = os.getenv("MAIN_CATEGORIES_DATABASE_ID")

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@timing_decorator
def get_sub_to_main_categories_mapping():
    """
    Creates a mapping of sub-categories to their corresponding main categories.

    This function fetches sub-categories from the Notion database and maps them to their
    respective main categories using another Notion database. The mapping is stored in a
    dictionary, where the keys are sub-category names and the values are main category names.

    Returns:
        dict: A dictionary where the keys are sub-category names and the values are the
            corresponding main category names.
    """
    pages = get_database(SUB_CATEGORIES_DATABASE_ID)

    maincategories_page_name_mapping = notion_utils.get_page_name_mapping(
        MAIN_CATEGORIES_DATABASE_ID
    )

    get_sub_to_main_categories_mapping_dict = {}
    for page in pages:
        try:
            # page_id = page["id"]
            props = page["properties"]
            if not props:
                pass

            name = props["Name"]["title"][0]["text"]["content"]
            main_category_info = notion_utils.extract_relation_type_info(
                props, "Main Finance Categories"
            )
            if main_category_info:
                main_category_id = main_category_info[0].get("id", None)
                main_category_name = maincategories_page_name_mapping.get(
                    main_category_id, None
                )
            else:
                main_category_id = None
                main_category_name = None

            get_sub_to_main_categories_mapping_dict[name] = main_category_name
        except:
            _logger.debug("Trouble adding page: %s", page)

    return get_sub_to_main_categories_mapping_dict


@timing_decorator
def get_finance_tracker_pages():
    pages = get_database(FINANCE_TRACKER_DATABASE_ID)
    return pages


@timing_decorator
def get_finance_tracker_df():
    """
    Fetches data from the finance tracker Notion database and converts it into a Pandas DataFrame,
    using cached data if it hasn't changed.

    The function retrieves financial data, including the name, date, amount, account, cash flow
    type, and category information. It maps sub-categories to main categories and organizes the
    data into a structured DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing financial data with the following columns:
        ['name', 'date', 'amount', 'account', 'cash_flow_type', 'business_related',
        'sub_category', 'main_category'].
    """
    load_dotenv()

    subcategories_page_name_mapping = notion_utils.get_page_name_mapping(
        SUB_CATEGORIES_DATABASE_ID
    )
    get_sub_to_main_categories_mapping_dict = get_sub_to_main_categories_mapping()

    pages = get_finance_tracker_pages()

    page_dicts = []
    for page in pages:
        try:
            page_dict = {}

            # page_id = page["id"]
            props = page["properties"]
            if not props:
                pass

            # Get all properties for each page and put in page_dict
            page_dict["name"] = props["Name"]["title"][0]["text"]["content"]
            date = props["Date"]["date"]["start"]
            page_dict["date"] = datetime.fromisoformat(date)
            page_dict["amount"] = notion_utils.extract_number_type_info(props, "Amount")
            page_dict["account"] = notion_utils.extract_select_type_info(
                props, "Account"
            )
            page_dict["cash_flow_type"] = notion_utils.extract_select_type_info(
                props, "Cash Flow Type"
            )
            page_dict["business_related"] = notion_utils.extract_select_type_info(
                props, "Business Related?"
            )
            sub_category_info = notion_utils.extract_relation_type_info(
                props, "Sub Category"
            )
            if sub_category_info:
                sub_category_id = sub_category_info[0].get("id", None)
                sub_category_name = subcategories_page_name_mapping.get(
                    sub_category_id, None
                )
            else:
                sub_category_name = None
            page_dict["sub_category"] = sub_category_name
            page_dict["main_category"] = get_sub_to_main_categories_mapping_dict.get(
                sub_category_name, None
            )
            page_dicts.append(page_dict)
        except:
            _logger.debug("Trouble adding page: %s", page)

    df = pd.DataFrame.from_dict(page_dicts)

    return df
