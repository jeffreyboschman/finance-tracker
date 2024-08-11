import pandas as pd

import finance_tracker.graphs.utils as graph_utils
from finance_tracker.connectors.notion_to_pandas import get_full_df


def graph_business_related_transfer_to_savings_totals(
    df: pd.DataFrame, write: bool = False
) -> None:
    """Generates a bar chart of business-related transfers to savings monthly totals and
    optionally saves it as an HTML file

    This function filters the provided DataFrame to include only business-related entries with
    the "Transfer to Savings" cash flow type. It calculates the total accumulated savings and
    creates a bar chart showing the monthly totals of these transfers. The chart can either
    be displayed interactively or saved as an HTML file. An annotation displaying the total
    accumulated amount is added to the chart.

    Args:
        df (pd.DataFrame): The input DataFrame containing cash flow data, including columns for
            ['date', 'business_related', 'cash_flow_type', 'amount', 'name']
        write (bool, optional): If True, saves the chart as an HTML file. If False, displays the
            chart interactively. Defaults to False.
    """
    df = graph_utils.preprocess_business_data(df)

    savings_df = df[df["cash_flow_type"] == "Transfer to Savings"]

    fig = graph_utils.plot_basic_monthly_bar_chart(
        savings_df, "Business-Related Tranfer to Savings (Monthly Totals)"
    )

    # Add an annotation displaying the total accumulated amount
    total_accumulated = savings_df["amount"].sum()
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
    graph_utils.display_or_write_chart(fig, write)


if __name__ == "__main__":
    full_df = get_full_df()
    graph_business_related_transfer_to_savings_totals(full_df, write=False)
