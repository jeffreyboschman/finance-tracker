import argparse

import pandas as pd
import plotly.express as px

import finance_tracker.graphs.utils as graph_utils
from finance_tracker.connectors.notion_to_pandas import get_finance_tracker_df


def _filter_and_prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters and prepares the DataFrame for graphing by sub-category.

    This function filters the input DataFrame to include only non-business-related expenses,
    converts the 'date' column to a monthly period, and groups the data by 'month_year',
    'main_category', and 'sub_category' to calculate the total amount spent in each sub-category
    for each month. It also calculates the total amount spent in each main category per month and
    the overall monthly total for all categories.

    Args:
        df (pd.DataFrame): The input DataFrame containing financial data with at least the
            following columns: ['date', 'business_related', 'cash_flow_type', 'amount',
            'main_category', 'sub_category'].

    Returns:
        pd.DataFrame: A DataFrame grouped by 'month_year', 'main_category', and 'sub_category',
        with additional columns for 'main_category_sum' (total amount spent in the main category
        per month), 'amount_monthly_total' (total amount spent across all categories per month),
        and 'color' (mapped from 'main_category' for consistent coloring in charts).
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

    # Calculate the total amount spent per month
    monthly_total = grouped_df.groupby("month_year")["amount"].sum().reset_index()

    # Merge the main category sum back into the grouped DataFrame
    grouped_df = pd.merge(
        grouped_df, main_category_sum, on=["month_year", "main_category"], how="left"
    )
    grouped_df = pd.merge(
        grouped_df,
        monthly_total,
        on="month_year",
        how="left",
        suffixes=("", "_monthly_total"),
    )

    # Sort values by main_category and sub_category
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
    print(grouped_df.head(40))
    print("\n\n")

    return grouped_df


def _create_stacked_bar_chart(
    grouped_df: pd.DataFrame, write: bool, chart_filename: str
) -> None:
    """
    Creates and displays or writes a stacked bar chart of sub-category totals.

    This function generates a stacked bar chart showing the total amount spent in each
    sub-category per month. The bars are colored according to the main category of each
    sub-category. Annotations are added above each bar to indicate the total sum of all
    expenses for that month. The chart can either be displayed interactively or saved as
    an HTML file.

    Args:
        grouped_df (pd.DataFrame): A grouped DataFrame containing columns for 'month_year',
            'main_category', 'sub_category', 'amount', 'main_category_sum', 'amount_monthly_total',
            and 'color'.
        write (bool): If True, saves the chart as an HTML file. If False, displays the chart
            interactively.
        chart_filename (str): The name of the HTML file to write to, if `write` is True.

    Returns:
        None
    """
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
    monthly_total = grouped_df.groupby("month_year")["amount"].sum().reset_index()
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


def _create_percent_stacked_bar_chart(
    grouped_df: pd.DataFrame, write: bool, chart_filename: str
) -> None:
    """
    Creates and displays or writes a percent-stacked bar chart of sub-category percentages.

    This function generates a percent-stacked bar chart showing the percentage of the total
    amount spent in each sub-category per month. The bars are colored according to the main
    category of each sub-category. Hover data includes the actual amount spent in each sub-category,
    the total amount spent in the associated main category, and the percentage of the total spent
    in the main category. The chart can either be displayed interactively or saved as an HTML file.

    Args:
        grouped_df (pd.DataFrame): A grouped DataFrame containing columns for 'month_year',
            'main_category', 'sub_category', 'amount', 'main_category_sum', 'amount_monthly_total',
            'percentage', 'main_category_percentage', and 'color'.
        write (bool): If True, saves the chart as an HTML file. If False, displays the chart
            interactively.
        chart_filename (str): The name of the HTML file to write to, if `write` is True.

    Returns:
        None
    """
    # Calculate the percentage of total amount for each sub-category
    grouped_df["percentage"] = (
        grouped_df["amount"] / grouped_df["amount_monthly_total"]
    ) * 100

    # Calculate the percentage of the main category's total amount
    grouped_df["main_category_percentage"] = (
        grouped_df["main_category_sum"] / grouped_df["amount_monthly_total"] * 100
    )

    fig = px.bar(
        grouped_df,
        x="month_year",
        y="percentage",
        color="sub_category",
        hover_data={
            "amount": ":.2f",
            "main_category_sum": ":.2f",
            "main_category_percentage": ":.2f",
            "main_category": True,
            "percentage": ":.2f",
            "month_year": False,
        },
        labels={"percentage": "Percentage Spent (%)", "month_year": "Month-Year"},
        category_orders={"sub_category": grouped_df["sub_category"].unique()},
    )

    # print(grouped_df.head(40))
    # # Customize hover template
    # fig.update_traces(
    #     hovertemplate=(
    #         "<b>%{data.name}</b><br>"
    #         "¥%{customdata[0]:,.2f}<br>"
    #         "%{y:.2f}%<br><br>"

    #         "Main Category: %{customdata[1]}<br>"
    #         "Main Category Total: ¥%{customdata[2]:,.2f}<br>"
    #         "Main Category %: %{customdata[3]:.2f}%<br>"
    #         "<extra></extra>"
    #     ),
    #     customdata=grouped_df[
    #         ["amount", "main_category", "main_category_sum", "main_category_percentage"]
    #     ].values,
    # )

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

    fig.update_layout(
        xaxis={"showgrid": False}, yaxis={"showgrid": False}, yaxis_tickformat="%"
    )
    graph_utils.display_or_write_chart(fig, write, chart_filename)


def graph_nonbusiness_related_subcategory_totals(
    df: pd.DataFrame,
    write: bool = False,
    chart_filename: str = "chart.html",
) -> None:
    """
    Generates a stacked bar chart of non-business-related expense totals by sub-category.

    This function filters the provided DataFrame to include only non-business-related expenses,
    groups the data by month and sub-category, and creates a stacked bar chart displaying the total
    amount spent in each sub-category for each month. The bars are colored according to the main
    category of each sub-category, and an annotation showing the total sum of all expenses for each
    month is added above the corresponding bar. The chart can either be displayed interactively or
    saved as an HTML file.

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
    grouped_df = _filter_and_prepare_data(df)
    _create_stacked_bar_chart(grouped_df, write, chart_filename)


def graph_nonbusiness_related_subcategory_percentages(
    df: pd.DataFrame,
    write: bool = False,
    chart_filename: str = "percent_chart.html",
) -> None:
    """
    Generates a percent-stacked bar chart of non-business-related expense totals by sub-category.

    This function filters the provided DataFrame to include only non-business-related expenses,
    groups the data by month and sub-category, and creates a percent-stacked bar chart displaying
    the percentage of the total amount spent in each sub-category for each month. The bars are
    colored according to the main category of each sub-category, and the chart can either be
    displayed interactively or saved as an HTML file.

    Args:
        df (pd.DataFrame): The input DataFrame containing financial data with at least the
            following columns: ['date', 'business_related', 'cash_flow_type', 'amount',
            'main_category', 'sub_category'].
        write (bool, optional): If True, saves the chart as an HTML file. If False, displays the
            chart interactively. Defaults to False.
        chart_filename (str, optional): The name of the HTML file to write to. Defaults to
            'percent_chart.html'.

    Returns:
        None
    """
    grouped_df = _filter_and_prepare_data(df)
    _create_percent_stacked_bar_chart(grouped_df, write, chart_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate financial graphs based on expenses."
    )
    parser.add_argument(
        "--chart_type",
        type=str,
        choices=["stacked", "percent"],
        default="stacked",
        help="Type of chart to generate: 'stacked' for a regular stacked bar chart, 'percent' for"
        "a percent-stacked bar chart.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="If specified, the chart will be saved as an HTML file. Otherwise, it will be"
        "displayed interactively.",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default="chart.html",
        help="Filename for the output HTML file if --write is specified. Defaults to 'chart.html'.",
    )

    args = parser.parse_args()

    full_df = get_finance_tracker_df()

    if args.chart_type == "stacked":
        graph_nonbusiness_related_subcategory_totals(
            df=full_df,
            write=args.write,
            chart_filename=args.filename,
        )
    elif args.chart_type == "percent":
        graph_nonbusiness_related_subcategory_percentages(
            df=full_df,
            write=args.write,
            chart_filename=args.filename,
        )
