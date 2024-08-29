import pandas as pd
import plotly.graph_objects as go

import finance_tracker.graphs.utils as graph_utils
from finance_tracker.connectors.notion_to_pandas import get_finance_tracker_df


def graph_business_related_expense_vs_revenue_totals(
    df: pd.DataFrame,
) -> go.Figure:
    """Generates a bar chart of business-related expenses vs. revenue monthly totals.

    This function filters the provided DataFrame to include only business-related entries,
    then gets the rows corresponding to "Revenue", "Expense", and "Transfer to Savings" cash flow
    types. It then creates a bar chart showing the monthly totals for each category, where
    "Transfer to Savings" is visualized as an "Expense". An annotation displaying the total
    'Profit' amount (after transferring to savings) is added to the chart.

    Args:
        df (pd.DataFrame): The input DataFrame containing cash flow data, including columns for
            ['date', 'business_related', 'cash_flow_type', 'amount', 'name']
    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
    """
    df = graph_utils.preprocess_business_data(df)

    # Separate data for revenue and expense
    # ("Transfer to Savings" will be visualized as an "Expense")
    revenue_df = df[df["cash_flow_type"] == "Revenue"]
    expense_df = df[df["cash_flow_type"] == "Expense"]
    transfer_to_savings_df = df[df["cash_flow_type"] == "Transfer to Savings"]
    transfer_to_savings_df.loc[:, "cash_flow_type"] = "Expense"

    # Create a combined DataFrame for plotting
    combined_df = pd.concat([revenue_df, expense_df, transfer_to_savings_df])

    fig = graph_utils.plot_basic_monthly_bar_chart(
        combined_df, "Business-Related Expense vs Revenue (Monthly Totals)"
    )

    # Add an annotation displaying the total `profit`
    total_revenue = revenue_df["amount"].sum()
    total_expenses = expense_df["amount"].sum()
    total_transfer_to_savings = transfer_to_savings_df["amount"].sum()
    total_profit = total_revenue - total_expenses - total_transfer_to_savings

    fig.add_annotation(
        text=f"Total 'Profit' (after transferring to savings): ¥{total_profit:,.2f}",
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
    return fig
