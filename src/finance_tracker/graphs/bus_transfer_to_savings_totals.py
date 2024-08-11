import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

import finance_tracker.graphs.utils as graph_utils
from finance_tracker.connectors.notion_api import get_database
from finance_tracker.connectors.notion_to_pandas import get_pandas_df


def graph_business_related_transfer_to_savings_totals(
    df: pd.DataFrame, write: bool = False
):
    """Good one"""
    df = df.copy()
    df = df[(df["business_related"] == "Business-Related")]
    df["date"] = pd.to_datetime(df["date"])
    df["month_year"] = df["date"].dt.to_period("M").astype(str)

    savings_df = df[df["cash_flow_type"] == "Transfer to Savings"]

    total_accumulated = savings_df["amount"].sum()

    # Plot using Plotly Express
    fig = px.bar(
        savings_df,
        x="month_year",
        y="amount",
        color="cash_flow_type",
        color_discrete_map=graph_utils.CASH_FLOW_COLOR_MAP,
        title="Business-Related Tranfer to Savings (Monthly Totals)",
        hover_data={
            "name": True,
            "date": True,
            "amount": True,
            "month_year": False,
            "cash_flow_type": False,
        },
        category_orders={"month_year": sorted(df["month_year"].unique())},
        barmode="group",
    )

    fig.add_annotation(
        text=f"Total Accumulated: ¥{total_accumulated:,.2f}",
        xref="paper",
        yref="paper",
        x=1,
        y=1,
        showarrow=False,
        font={"size": 12, "color": "black"},
        bgcolor="white",
        bordercolor="black",
        borderwidth=1,
    )

    fig.update_xaxes(type="category")
    fig.update_layout(xaxis_tickangle=-45)

    if write:
        fig.write_html("chart.html")
    else:
        fig.show()


if __name__ == "__main__":
    load_dotenv()
    notion_db = get_database()
    df = get_pandas_df(notion_db)
    graph_business_related_transfer_to_savings_totals(df, write=False)
