import pandas as pd

import finance_tracker.graphs.utils as graph_utils
from finance_tracker.connectors.notion_to_pandas import get_full_df


def graph_business_related_expense_vs_revenue_totals(
    df: pd.DataFrame, write: bool = False
) -> None:
    """Generates a bar chart of business-related expenses vs. revenue monthly totals and
    optionally saves it as an HTML file.

    This function filters the provided DataFrame to include only business-related entries,
    then gets the rows corresponding to "Revenue", "Expense", and "Transfer to Savings" cash flow
    types. It then creates a bar chart showing the monthly totals for each category, where
    "Transfer to Savings" is visualized as an "Expense". The chart can either be displayed
    interactively or saved as an HTML file.

    Args:
        df (pd.DataFrame): The input DataFrame containing cash flow data, including columns for
            ['date', 'business_related', 'cash_flow_type', 'amount', 'name']
        write (bool, optional): If True, saves the chart as an HTML file. If False, displays the
            chart interactively. Defaults to False.
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

    graph_utils.display_or_write_chart(fig, write)


if __name__ == "__main__":
    full_df = get_full_df()
    graph_business_related_expense_vs_revenue_totals(full_df, write=False)
