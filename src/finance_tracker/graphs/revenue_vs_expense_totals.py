import pandas as pd
import plotly.graph_objects as go

import finance_tracker.graphs.utils as graph_utils


def graph_business_revenue_vs_expense_and_tax_totals(
    df: pd.DataFrame,
) -> go.Figure:
    """Generates a bar chart of business revenue vs expense monthly totals.

    This function filters the provided DataFrame to include only business-related entries,
    then gets the rows corresponding to "Revenue", "Expense", and "Reserved for Taxes" cash flow
    types. It then creates a bar chart showing the monthly totals for each category, where
    "Reserved for Taxes" is visualized as an "Expense". An annotation displaying the Total
    After-Tax Working Capital amount is added to the chart.

    Args:
        df (pd.DataFrame): The input DataFrame containing cash flow data, including columns for
            ['date', 'business_related', 'cash_flow_type', 'amount', 'name']
    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
    """
    # Preprocessing
    df = df.copy()
    df = df[df["business_related"] == "Business-Related"]
    df = graph_utils.add_month_year_column(df)

    # Separate data for revenue and expense and create a combined df
    # ("Reserved for Taxes" will be visualized as an "Expense")
    revenue_df = df[df["cash_flow_type"] == "Revenue"]
    expense_df = df[df["cash_flow_type"] == "Expense"]
    taxes_df = df[df["cash_flow_type"] == "Reserved for Taxes"]
    taxes_df.loc[:, "cash_flow_type"] = "Expense"
    combined_df = pd.concat([revenue_df, expense_df, taxes_df])

    # Create basic plot
    fig = graph_utils.plot_basic_monthly_bar_chart(
        combined_df, "Business Revenue vs Expense (and Tax) - Totals"
    )

    # Add annotations for monthly totals
    fig = graph_utils.add_monthly_total_annotations(
        fig, combined_df, "amount", "cash_flow_type"
    )

    # Add an annotation displaying the total working capital
    total_revenue = revenue_df["amount"].sum()
    total_expenses = expense_df["amount"].sum()
    total_taxes = taxes_df["amount"].sum()
    total_working_capital = total_revenue - total_expenses - total_taxes
    working_capital_annotation_text = (
        f"Total After-Tax Working Capital: ¥{total_working_capital:,.2f}"
    )
    fig = graph_utils.add_single_annotation(fig, working_capital_annotation_text, y=1.2)

    # Add an annotation displaying the total reserved for taxes
    taxes_annotation_text = f"Total Reserved for Taxes: ¥{total_taxes:,.2f}"
    fig = graph_utils.add_single_annotation(fig, taxes_annotation_text, y=1.1)

    return fig


def graph_personal_revenue_vs_expense_and_saving_totals(
    df: pd.DataFrame,
) -> go.Figure:
    """Generates a bar chart of personal expenses vs. revenue monthly totals.

    This function filters the provided DataFrame to include only non-business-related entries,
    then gets the rows corresponding to "Revenue", "Expense", and "Transfer to Savings" cash flow
    types. It then creates a bar chart showing the monthly totals for each category, where
    "Transfer to Savings" is visualized as an "Expense". An annotation displaying the Total
    After-Tax Working Capital amount is added to the chart.

    Args:
        df (pd.DataFrame): The input DataFrame containing cash flow data, including columns for
            ['date', 'business_related', 'cash_flow_type', 'amount', 'name']
    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
    """
    # Preprocessing
    df = df.copy()
    df = df[df["business_related"] == "Not Business-Related"]
    df = graph_utils.add_month_year_column(df)

    # Separate data for revenue and expense and create a combined df
    # ("Reserved for Taxes" will be visualized as an "Expense")
    revenue_df = df[df["cash_flow_type"] == "Revenue"]
    expense_df = df[df["cash_flow_type"] == "Expense"]
    savings_df = df[df["cash_flow_type"] == "Transfer to Savings"]
    savings_df.loc[:, "cash_flow_type"] = "Expense"
    combined_df = pd.concat([revenue_df, expense_df, savings_df])

    # Create basic plot
    fig = graph_utils.plot_basic_monthly_bar_chart(
        combined_df, "Personal Revenue vs Expense (and Saving) - Totals"
    )

    # Add annotations for monthly totals
    fig = graph_utils.add_monthly_total_annotations(
        fig, combined_df, "amount", "cash_flow_type"
    )

    # Add an annotation displaying the total working capital
    total_revenue = revenue_df["amount"].sum()
    total_expenses = expense_df["amount"].sum()
    total_savings = savings_df["amount"].sum()
    total_working_capital = total_revenue - total_expenses - total_savings
    working_capital_annotation_text = (
        f"Total Personal Wiggle Room: ¥{total_working_capital:,.2f}"
    )
    fig = graph_utils.add_single_annotation(fig, working_capital_annotation_text, y=1.2)

    # Add an annotation displaying the total savings
    savings_annotation_text = f"Total Savings: ¥{total_savings:,.2f}"
    fig = graph_utils.add_single_annotation(fig, savings_annotation_text, y=1.1)

    return fig
