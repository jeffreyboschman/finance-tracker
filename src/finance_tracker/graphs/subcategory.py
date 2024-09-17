import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import finance_tracker.graphs.utils as graph_utils


def _filter_and_prepare_data(
    df: pd.DataFrame, business_related: str, cash_flow_types: list[str]
) -> pd.DataFrame:
    """
    Filters and prepares the DataFrame for graphing by sub-category.

    This function filters the input DataFrame based on the specified business-related status
    and a list of cash flow types, converts the 'date' column to a monthly period, and groups
    the data by 'month_year', 'main_category', and 'sub_category' to calculate the total amount
    spent in each sub-category for each month. It also calculates the total amount spent in each
    main category per month and the overall monthly total for all categories.

    Args:
        df (pd.DataFrame): The input DataFrame containing financial data with at least the
            following columns: ['date', 'business_related', 'cash_flow_type', 'amount',
            'main_category', 'sub_category'].
        business_related (str): The business-related status to filter by (e.g., "Not
            Business-Related").
        cash_flow_types (list): A list of cash flow types to filter by (e.g., ["Expense",
            "Revenue"]).

    Returns:
        pd.DataFrame: A DataFrame grouped by 'month_year', 'main_category', and 'sub_category',
        with additional columns for 'main_category_sum' (total amount spent in the main category
        per month), 'amount_monthly_total' (total amount spent across all categories per month),
        and 'color' (mapped from 'main_category' for consistent coloring in charts).
    """
    df = df.copy()
    df = df[df["business_related"] == business_related]
    df = graph_utils.add_month_year_column(df)
    df = df[df["cash_flow_type"].isin(cash_flow_types)]

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

    return grouped_df


def _create_stacked_bar_chart(grouped_df: pd.DataFrame, title: str) -> go.Figure:
    """
    Creates a plotly stacked bar chart of sub-category totals.

    This function generates a stacked bar chart showing the total amount spent in each
    sub-category per month. The bars are colored according to the main category of each
    sub-category. Annotations are added above each bar to indicate the total sum of all
    expenses for that month.

    Args:
        grouped_df (pd.DataFrame): A grouped DataFrame containing columns for 'month_year',
            'main_category', 'sub_category', 'amount', 'main_category_sum', 'amount_monthly_total',
            and 'color'.
        title (str): The title of the chart.

    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
    """
    fig = px.bar(
        grouped_df,
        x="month_year",
        y="amount",
        color="sub_category",
        title=title,
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
    fig = graph_utils.add_monthly_total_annotations(fig, grouped_df, "amount")

    fig.update_layout(xaxis={"showgrid": False}, yaxis={"showgrid": False})
    return fig


def _create_percent_stacked_bar_chart(grouped_df: pd.DataFrame) -> go.Figure:
    """
    Creates a plotly percent-stacked bar chart of sub-category percentages.

    This function generates a percent-stacked bar chart showing the percentage of the total
    amount spent in each sub-category per month. The bars are colored according to the main
    category of each sub-category. Hover data includes the actual amount spent in each sub-category,
    the total amount spent in the associated main category, and the percentage of the total spent
    in the main category.

    Args:
        grouped_df (pd.DataFrame): A grouped DataFrame containing columns for 'month_year',
            'main_category', 'sub_category', 'amount', 'main_category_sum', 'amount_monthly_total',
            'percentage', 'main_category_percentage', and 'color'.

    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
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
        xaxis={"showgrid": False}, yaxis={"showgrid": True}, yaxis_tickformat="%"
    )
    return fig


# Business graphs


def graph_business_expenses_and_taxes_by_subcategory(
    df: pd.DataFrame,
) -> go.Figure:
    """
    Generates a stacked bar chart of business expense and tax totals by sub-category.

    Args:
        df (pd.DataFrame): The input DataFrame containing financial data with at least the
            following columns: ['date', 'business_related', 'cash_flow_type', 'amount',
            'main_category', 'sub_category'].

    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
    """
    grouped_df = _filter_and_prepare_data(
        df, "Business-Related", ["Expense", "Reserved for Taxes"]
    )
    return _create_stacked_bar_chart(grouped_df, "Business Expenses - By Category")


def graph_business_expenses_by_subcategory(
    df: pd.DataFrame,
) -> go.Figure:
    """
    Generates a stacked bar chart of business expense totals by sub-category.

    Args:
        df (pd.DataFrame): The input DataFrame containing financial data with at least the
            following columns: ['date', 'business_related', 'cash_flow_type', 'amount',
            'main_category', 'sub_category'].

    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
    """
    grouped_df = _filter_and_prepare_data(df, "Business-Related", ["Expense"])
    return _create_stacked_bar_chart(grouped_df, "Business Expenses - By Category")


def graph_business_revenue_by_subcategory(
    df: pd.DataFrame,
) -> go.Figure:
    """
    Generates a stacked bar chart of business revenue totals by sub-category.

    Args:
        df (pd.DataFrame): The input DataFrame containing financial data with at least the
            following columns: ['date', 'business_related', 'cash_flow_type', 'amount',
            'main_category', 'sub_category'].

    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
    """
    grouped_df = _filter_and_prepare_data(df, "Business-Related", ["Revenue"])
    return _create_stacked_bar_chart(grouped_df, "Business Revenue - By Category")


# Personal graphs


def graph_personal_expenses_and_savings_by_subcategory(
    df: pd.DataFrame,
) -> go.Figure:
    """
    Generates a stacked bar chart of personal expense and savings totals by sub-category.

    Args:
        df (pd.DataFrame): The input DataFrame containing financial data with at least the
            following columns: ['date', 'business_related', 'cash_flow_type', 'amount',
            'main_category', 'sub_category'].

    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
    """
    grouped_df = _filter_and_prepare_data(
        df, "Not Business-Related", ["Expense", "Transfer to Savings"]
    )
    return _create_stacked_bar_chart(
        grouped_df, "Personal Expenses and Savings - By Category"
    )


def graph_personal_expenses_by_subcategory(
    df: pd.DataFrame,
) -> go.Figure:
    """
    Generates a stacked bar chart of non-business-related expense totals by sub-category.

    Args:
        df (pd.DataFrame): The input DataFrame containing financial data with at least the
            following columns: ['date', 'business_related', 'cash_flow_type', 'amount',
            'main_category', 'sub_category'].

    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
    """
    grouped_df = _filter_and_prepare_data(df, "Not Business-Related", ["Expense"])
    return _create_stacked_bar_chart(grouped_df, "Personal Expenses - By Category")


def graph_personal_revenue_by_subcategory(
    df: pd.DataFrame,
) -> go.Figure:
    """
    Generates a stacked bar chart of non-business-related expense totals by sub-category.

    Args:
        df (pd.DataFrame): The input DataFrame containing financial data with at least the
            following columns: ['date', 'business_related', 'cash_flow_type', 'amount',
            'main_category', 'sub_category'].

    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
    """
    grouped_df = _filter_and_prepare_data(df, "Not Business-Related", ["Revenue"])
    return _create_stacked_bar_chart(grouped_df, "Personal Revenue - By Category")
