import pandas as pd
import plotly.graph_objects as go

import finance_tracker.graphs.utils as graph_utils
from finance_tracker.connectors.notion_to_pandas import get_finance_tracker_df


def graph_business_related_transfer_to_savings_totals(
    df: pd.DataFrame,
) -> go.Figure:
    """Generates a bar chart of business-related transfers to savings monthly totals.

    This function filters the provided DataFrame to include only business-related entries with
    the "Transfer to Savings" cash flow type. It calculates the total accumulated savings and
    creates a bar chart showing the monthly totals of these transfers. An annotation displaying
    the total accumulated amount is added to the chart.

    Args:
        df (pd.DataFrame): The input DataFrame containing cash flow data, including columns for
            ['date', 'business_related', 'cash_flow_type', 'amount', 'name']
    Returns:
        go.Figure: A Plotly Figure object representing the bar chart of business-related transfers
        to savings monthly totals, with an annotation showing the total accumulated amount.
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
    return fig
