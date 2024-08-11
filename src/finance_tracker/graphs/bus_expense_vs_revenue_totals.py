import pandas as pd
import plotly.express as px

import finance_tracker.graphs.utils as graph_utils
from finance_tracker.connectors.notion_to_pandas import get_full_df


def graph_business_related_expense_vs_revenue_totals(
    df: pd.DataFrame, write: bool = False
):
    df = graph_utils.preprocess_business_data(df)

    # Separate data for revenue and expense
    revenue_df = df[df["cash_flow_type"] == "Revenue"]

    expense_df = df[df["cash_flow_type"] == "Expense"]
    transfer_to_savings_df = df[df["cash_flow_type"] == "Transfer to Savings"]
    transfer_to_savings_df.loc[:, "cash_flow_type"] = "Expense"

    # Create a combined DataFrame for plotting
    combined_df = pd.concat([revenue_df, expense_df, transfer_to_savings_df])

    # Plot using Plotly Express
    fig = px.bar(
        combined_df,
        x="month_year",
        y="amount",
        color="cash_flow_type",
        color_discrete_map=graph_utils.CASH_FLOW_COLOR_MAP,
        title="Business-Related Expense vs Revenue (Monthly Totals)",
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

    fig.update_xaxes(type="category")
    fig.update_layout(xaxis_tickangle=-45)

    if write:
        fig.write_html("chart.html")
    else:
        fig.show()


if __name__ == "__main__":
    full_df = get_full_df()
    graph_business_related_expense_vs_revenue_totals(full_df, write=False)
