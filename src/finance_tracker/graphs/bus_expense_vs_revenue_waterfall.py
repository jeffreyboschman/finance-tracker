import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

from finance_tracker.connectors.notion_api import get_database
from finance_tracker.connectors.notion_to_pandas import get_pandas_df


def graph_business_related_expense_vs_revenue_vs_savings_waterfall(
    df: pd.DataFrame, write: bool = False
):
    """
    Generates a waterfall graph of business-related expenses versus revenues
    and optionally saves it as an HTML file.

    This function filters the provided DataFrame for business-related transactions and
    aggregates the data into revenue and expense categories by date. Revenue amounts are
    halved, and expenses are made negative. The data is then aggregated by date, and a
    cumulative waterfall chart is generated using Plotly.

    Args:
        df (pd.DataFrame): The input DataFrame containing cash flow data with columns
            ['date', 'business_related', 'cash_flow_type', 'amount', 'name'].
        file_path (str, optional): The path to save the HTML file. If not provided,
            the plot will not be saved.

    Returns:
        None: This function displays a Plotly waterfall graph and optionally saves it as an
             HTML file.

    Raises:
        ValueError: If the 'date' column cannot be converted to datetime format.

    """
    df = df.copy()
    df = df[(df["business_related"] == "Business-Related")]
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")

    # Separate data for revenue and expense and savings
    revenue_df = df[df["cash_flow_type"] == "Revenue"]

    expense_df = df[df["cash_flow_type"] == "Expense"]
    expense_df.loc[:, "amount"] = -1 * (expense_df["amount"])

    savings_df = df[df["cash_flow_type"] == "Transfer to Savings"]
    savings_df.loc[:, "amount"] = -1 * (savings_df["amount"])

    # Create a combined DataFrame for plotting
    combined_df = pd.concat([expense_df, savings_df, revenue_df])

    def aggregate_names_amounts(group):
        return ", ".join(
            [
                f"{name} ({'+' if amount > 0 else ''}{amount})"
                for name, amount in zip(group["name"], group["amount"])
            ]
        )

    combined_agg_df = (
        combined_df.groupby("date", group_keys=False)
        .apply(
            lambda group: pd.Series(
                {
                    "amount": group["amount"].sum(),
                    "name": aggregate_names_amounts(group),
                }
            ),
            include_groups=False,
        )
        .reset_index()
    )

    combined_agg_df = combined_agg_df.sort_values(by="date")

    fig = go.Figure(
        go.Waterfall(
            name="20",
            orientation="v",
            x=combined_agg_df["date"],
            y=combined_agg_df["amount"],
            measure=["relative"] * len(combined_agg_df),
            textposition="outside",
            text=combined_agg_df["name"],
            hoverinfo="text",
            increasing={"marker": {"color": "#2CA02C"}},
            decreasing={"marker": {"color": "#EF553B"}},
        )
    )

    fig.update_layout(
        title="Business-Related Expense vs Revenue (Cumulative Waterfall)",
        xaxis_title="Date",
        yaxis_title="Amount (¥)",
        xaxis_tickangle=-45,
    )

    # if write:
    #     pio.write_html(fig, "chart.html", auto_open=False)

    if write:
        fig.write_html("chart.html")
    else:
        fig.show()


if __name__ == "__main__":
    load_dotenv()
    notion_db = get_database()
    df = get_pandas_df(notion_db)
    graph_business_related_expense_vs_revenue_vs_savings_waterfall(df, write=False)
