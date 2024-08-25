import pandas as pd
import plotly.express as px

import finance_tracker.graphs.utils as graph_utils
from finance_tracker.connectors.notion_to_pandas import get_finance_tracker_df


def graph_nonbusiness_related_subcategory_totals(
    df: pd.DataFrame,
    write: bool = False,
    chart_filename: str = "chart.html",
) -> None:
    """Generates a stacked bar chart of non-business-related expense totals by sub-category.

    This function filters the provided DataFrame to include only non-business-related expenses,
    groups the data by month and sub-category, and creates a stacked bar chart displaying
    the total amount spent in each sub-category for each month. The bars are colored according
    to the main category of each sub-category, and an annotation showing the total sum of all
    expenses for each month is added above the corresponding bar. The chart can either be
    displayed interactively or saved as an HTML file.

    Args:
        df (pd.DataFrame): The input DataFrame containing financial data with at least the
            following columns: ['date', 'business_related', 'cash_flow_type', 'amount',
            'main_category', 'sub_category'].
        write (bool, optional): If True, saves the chart as an HTML file. If False, displays the
            chart interactively. Defaults to False.
        chart_filename (str, optional): The name of the HTML file to write to. Defaults to
            'chart.html'.

    Returns:
        None
    """
    df = df.copy()
    df = df[df["business_related"] == "Not Business-Related"]
    df["date"] = pd.to_datetime(df["date"])
    df["month_year"] = df["date"].dt.to_period("M").astype(str)
    df = df[df["cash_flow_type"] == "Expense"]

    # Group by month_year, main_category, and sub_category
    grouped_df = df.groupby(
        ["month_year", "main_category", "sub_category"], as_index=False
    )["amount"].sum()

    # Calculate the sum for each main_category per month_year
    main_category_sum = (
        grouped_df.groupby(["month_year", "main_category"])["amount"]
        .sum()
        .reset_index()
    )
    main_category_sum.rename(columns={"amount": "main_category_sum"}, inplace=True)

    monthly_total = grouped_df.groupby("month_year")["amount"].sum().reset_index()

    # Merge the main category sum back into the original grouped DataFrame
    grouped_df = pd.merge(
        grouped_df, main_category_sum, on=["month_year", "main_category"], how="left"
    )
    grouped_df.sort_values(by=["main_category", "sub_category"], inplace=True)

    # Map sub_categories to the same color as their main_category
    grouped_df["color"] = grouped_df["main_category"].map(
        graph_utils.MAIN_FINANCE_CATEGORIES_COLOR_MAP
    )

    # Define the order of sub-categories within main categories
    grouped_df["sub_category"] = pd.Categorical(
        grouped_df["sub_category"],
        categories=grouped_df["sub_category"].unique(),
        ordered=True,
    )
    # Create the stacked bar chart
    fig = px.bar(
        grouped_df,
        x="month_year",
        y="amount",
        color="sub_category",
        hover_data={
            "main_category_sum": True,
            "main_category": True,
            "month_year": False,
        },
        labels={"amount": "Amount Spent", "month_year": "Month-Year"},
        category_orders={"sub_category": grouped_df["sub_category"].unique()},
    )

    # Update traces with custom colors
    for main_category in grouped_df["main_category"].unique():
        for trace in fig.data:
            if (
                trace.name
                in grouped_df.loc[
                    grouped_df["main_category"] == main_category, "sub_category"
                ].values
            ):
                trace.marker.color = graph_utils.MAIN_FINANCE_CATEGORIES_COLOR_MAP[
                    main_category
                ]

    # Add annotations for monthly totals
    for _, row in monthly_total.iterrows():
        fig.add_annotation(
            x=row["month_year"],
            y=row["amount"],
            text=f"{row['amount']:.2f}",  # Format the total sum as desired
            showarrow=False,
            yshift=10,  # Adjust position above the bar
            font={"size": 12, "color": "black"},
        )

    fig.update_layout(xaxis={"showgrid": False}, yaxis={"showgrid": False})
    graph_utils.display_or_write_chart(fig, write, chart_filename)


if __name__ == "__main__":
    full_df = get_finance_tracker_df()
    graph_nonbusiness_related_subcategory_totals(full_df, write=False)
