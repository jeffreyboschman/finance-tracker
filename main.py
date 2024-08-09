import requests
import json
from datetime import datetime, timezone
import pandas as pd
from dotenv import load_dotenv
import os
import notion_api as notion_api
import create_graphs as create_graphs

def get_database():
    pages = notion_api.get_pages()
    return pages

def get_pandas_df(pages):

    page_dicts = []
    for page in pages:
        page_dict = dict()

        page_id = page["id"]
        props = page["properties"]
        if not props:
            pass
            
        name = props["Name"]["title"][0]["text"]["content"]
        date = props["Date"]["date"]["start"]
        date = datetime.fromisoformat(date)
        amount = notion_api.extract_number_type_info(props, "Amount")
        account = notion_api.extract_select_type_info(props, "Account")
        cash_flow_type = notion_api.extract_select_type_info(props, "Cash Flow Type")
        business_related = notion_api.extract_select_type_info(props, "Business Related?")
        main_category = notion_api.extract_rollup_type_info(props, "Main Category")
        page_dict["name"] = name
        page_dict["date"] = date
        page_dict["amount"] = amount
        page_dict["account"] = account
        page_dict["cash_flow_type"] = cash_flow_type
        page_dict["business_related"] = business_related
        page_dicts.append(page_dict)

    df = pd.DataFrame.from_dict(page_dicts) 

    return df




if __name__ == "__main__":
    load_dotenv()
    notion_db = get_database()
    df = get_pandas_df(notion_db)
    # create_graphs.graph_prestia_cash_flow_in_out_for_month(df, "05", "2024")
    create_graphs.graph_business_related_expense_vs_revenue_totals(df)
    # create_graphs.graph_business_related_expense_vs_revenue_vs_savings_waterfall(df, "output.html")
    # create_graphs.graph_business_related_transfer_to_savings_totals(df)