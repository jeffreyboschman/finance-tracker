from datetime import datetime
import pandas as pd
from finance_tracker.connectors import notion_utils



def get_pandas_df(pages: dict):

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
        amount = notion_utils.extract_number_type_info(props, "Amount")
        account = notion_utils.extract_select_type_info(props, "Account")
        cash_flow_type = notion_utils.extract_select_type_info(props, "Cash Flow Type")
        business_related = notion_utils.extract_select_type_info(props, "Business Related?")
        main_category = notion_utils.extract_rollup_type_info(props, "Main Category")
        page_dict["name"] = name
        page_dict["date"] = date
        page_dict["amount"] = amount
        page_dict["account"] = account
        page_dict["cash_flow_type"] = cash_flow_type
        page_dict["business_related"] = business_related
        page_dicts.append(page_dict)

    df = pd.DataFrame.from_dict(page_dicts) 

    return df