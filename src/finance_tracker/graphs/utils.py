import calendar

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CASH_FLOW_COLOR_MAP = {
    "Revenue": "#4DAB9A",
    "Expense": "#FF7369",
    "Transfer to Savings": "#FFDC49",
    "Bank Transfer Out": "#FFA344",
    "Bank Transfer In": "#529CCA",
}
# Colors from:
# https://optemization.notion.site/b58409d4a92444368cbad42b60d9ea55?v=8de8c56bd44f4239ab7cd145c62d35c3

CASH_FLOW_PATTERN_MAP = {
    "Revenue": "",
    "Expense": "#FF7369",
    "Transfer to Savings": "#FFDC49",
    "Bank Transfer Out": "#FFA344",
    "Bank Transfer In": "#529CCA",
}

# Select LM (RGB) colors from
# https://optemization.notion.site/b58409d4a92444368cbad42b60d9ea55?v=d05b18c8bb8942c5b418dda9e0a060ff
MAIN_FINANCE_CATEGORIES_COLOR_MAP = {
    "Food": "rgba(255,0,26,0.2)",  # red
    "Entertainment": "rgba(0,120,223,0.2)",  # blue
    "Housing": "rgba(245,93,0,0.2)",  # orange
    "Transportation": "rgba(103,36,222,0.2)",  # purple
    "Family and Friends": "rgba(0,120,223,0.2)",  # blue
    "Government": "rgba(206,205,202,0.5)",  # black/white
    "Finance": "rgba(0,135,107,0.2)",  # green
    "Health and Wellness": "rgba(255,220,73,0.5)",  # yellow
    "Utilities": "rgba(155,154,151,0.4)",  # grey
    "Investments": "rgba(221,0,129,0.2)",  # pink
    "Career Related": "rgba(140,46,0,0.2)",  # brown
    "Digital Services/Products/Tools": "rgba(206,205,202,0.5)",  # black/white
}


def get_days_in_month(year: int, month: int) -> list[int]:
    """Get a list of all the days in a given month.

    This function calculates the number of days in the specified month of the specified year
    and returns a list of all the days in that month.

    Args:
        year (int): The year as a four-digit number (e.g., 2024).
        month (int): The month as a number (1-12).

    Returns:
        list[int]: A list of integers representing all the days in the specified month.
    """
    num_days = calendar.monthrange(year, month)[1]
    days_in_month = list(range(1, num_days + 1))
    return days_in_month


def preprocess_business_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the DataFrame by filtering business-related entries and creating the
    'month_year' column.

    This function filters the input DataFrame to include only rows marked as "Business-Related"
    and creates a new 'month_year' column based on the 'date' column. The 'date' column is
    converted to datetime format.

    Args:
        df (pd.DataFrame): The input DataFrame containing financial data with columns
            ['date', 'business_related']

    Returns:
        pd.DataFrame: A new DataFrame with only business-related entries and a 'month_year'
            column.
    """
    df = df.copy()
    df = df[df["business_related"] == "Business-Related"]
    df["date"] = pd.to_datetime(df["date"])
    df["month_year"] = df["date"].dt.to_period("M").astype(str)
    return df


def display_or_write_chart(
    fig: go.Figure, write: bool = False, file_name: str = "chart.html"
) -> None:
    """Display the Plotly figure or write it to an HTML file.

    This function either displays the provided Plotly figure interactively or saves it as
    an HTML file, depending on the value of the 'write' argument.

    Args:
        fig (go.Figure): The Plotly figure to be displayed or written.
        write (bool, optional): If True, writes the figure to an HTML file. Defaults to False.
        file_name (str, optional): The name of the HTML file to write to. Defaults to 'chart.html'.
    """
    if write:
        fig.write_html(file_name)
    else:
        fig.show()


def plot_basic_monthly_bar_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """Plot a bar chart using Plotly Express.

    This function generates a grouped bar chart showing the monthly totals of different
    cash flow types from the input DataFrame. The chart is customized with hover data,
    category orders, and a specified title.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be plotted, including columns for
            [ 'name', 'date', 'amount', 'month_year', 'cash_flow_type']
        title (str): The title of the chart.

    Returns:
        go.Figure: The generated Plotly figure for the bar chart.
    """
    fig = px.bar(
        df,
        x="month_year",
        y="amount",
        color="cash_flow_type",
        color_discrete_map=CASH_FLOW_COLOR_MAP,
        title=title,
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

    return fig
