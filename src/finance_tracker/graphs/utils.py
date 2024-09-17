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
    "Housing": "rgba(245,93,0,0.2)",  # orange
    "Household Goods": "rgba(221,0,129,0.2)",  # pink
    "Food": "rgba(255,0,26,0.2)",  # red
    "Entertainment": "rgba(0,120,223,0.2)",  # blue
    "Utilities": "rgba(155,154,151,0.4)",  # grey
    "Health and Wellness": "rgba(255,220,73,0.5)",  # yellow
    "Career Related": "rgba(140,46,0,0.2)",  # brown
    "Transportation": "rgba(103,36,222,0.2)",  # purple
    "Digital Services/Products/Tools": "rgba(206,205,202,0.5)",  # black/white
    "Finance": "rgba(0,135,107,0.2)",  # green
    "Family and Friends": "rgba(221,0,129,0.2)",  # pink
    "Government": "rgba(206,205,202,0.5)",  # black/white
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


def add_month_year_column(df: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    """Adds a 'month_year' column to the DataFrame based on the specified date column.

    This function converts the specified date column to datetime format and creates a new
    'month_year' column representing the year and month of each date.

    Args:
        df (pd.DataFrame): The input DataFrame containing a date column.
        date_column (str): The name of the date column to be used for creating the 'month_year'
            column.

    Returns:
        pd.DataFrame: A new DataFrame with the 'month_year' column added.
    """
    df[date_column] = pd.to_datetime(df[date_column])
    df["month_year"] = df[date_column].dt.to_period("M").astype(str)
    return df


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


# pylint: disable=too-many-arguments
def add_single_annotation(
    fig: go.Figure,
    text: str,
    x: float = 1,
    y: float = 1.1,
    font_size: int = 12,
    font_color: str = "black",
    bgcolor: str = "white",
    bordercolor: str = "black",
    borderwidth: int = 1,
) -> go.Figure:
    """Adds a single annotation on a Plotly figure.

    This function adds an annotation to the specified Plotly figure with customizable text and
    other styling parameters.

    Args:
        fig (go.Figure): The Plotly figure to which the annotation will be added.
        text (str): The text for the annotation.
        x (float): The x-coordinate for the annotation (default is 1, which is the far right).
        y (float): The y-coordinate for the annotation (default is 1.1, which is right above
            the top).
        font_size (int): The font size of the annotation text (default is 12).
        font_color (str): The color of the annotation text (default is "black").
        bgcolor (str): The background color of the annotation (default is "white").
        bordercolor (str): The border color of the annotation (default is "black").
        borderwidth (int): The border width of the annotation (default is 1).

    Returns:
        go.Figure: The Plotly figure with the annotation added.
    """
    fig.add_annotation(
        text=text,
        xref="paper",
        yref="paper",
        x=x,
        y=y,
        showarrow=False,
        font={"size": font_size, "color": font_color},
        bgcolor=bgcolor,
        bordercolor=bordercolor,
        borderwidth=borderwidth,
    )
    return fig


def add_monthly_total_annotations(
    fig: go.Figure,
    df: pd.DataFrame,
    y_column: str = "amount",
    extra_x_group: str | None = None,
) -> go.Figure:
    """
    Adds annotations for monthly totals to a Plotly figure.

    This function can add annotations for either the total amount per month or for each
    subgroup within a month, depending on the presence of an extra grouping column.

    Args:
        fig (go.Figure): The Plotly figure to which annotations will be added.
        df (pd.DataFrame): A DataFrame containing at least 'month_year' and the specified y_column.
            If extra_x_group is provided, the DataFrame should also contain that column.
        y_column (str): The column name in df that contains the values to be summed for annotations.
        extra_x_group (str | None): An optional column name for additional grouping within each
            month_year. If provided, annotations will be added for each subgroup within each month.

    Returns:
        go.Figure: The Plotly figure with annotations added.
    """
    if extra_x_group:
        monthly_totals = (
            df.groupby(["month_year", extra_x_group])[y_column].sum().reset_index()
        )

        # Get unique cash flow types and their positions
        unique_x_groups = df[extra_x_group].unique()
        num_x_groups = len(unique_x_groups)

        # Calculate the width of each bar and the spacing between bars
        bar_width = 1 / (num_x_groups)
        spacing = bar_width / 2  # Adjust as needed for spacing

        group_positions = {x_group: i for i, x_group in enumerate(unique_x_groups)}

        for _, row in monthly_totals.iterrows():
            # Calculate the x offset based on the cash flow type position
            # x_offset = (
            #     group_positions[row[extra_x_group]] - (num_x_groups - 1) / 2
            # ) * 0.7  # Adjust 0.7 as needed for spacing
            x_offset = (
                group_positions[row[extra_x_group]] - (num_x_groups - 1) / 2
            ) * (bar_width + spacing)

            fig.add_annotation(
                x=row["month_year"],
                y=row[y_column],
                xshift=x_offset * 100,  # Convert to pixels for xshift
                text=f"¥{row[y_column]:.0f}",  # Format the total sum as desired
                showarrow=False,
                yshift=10,  # Adjust position above the bar
                font={"size": 12, "color": "black"},
            )

    else:
        monthly_total = df.groupby("month_year")[y_column].sum().reset_index()
        for _, row in monthly_total.iterrows():
            fig.add_annotation(
                x=row["month_year"],
                y=row[y_column],
                text=f"¥{row[y_column]:.0f}",  # Format the total sum as desired
                showarrow=False,
                yshift=10,  # Adjust position above the bar
                font={"size": 12, "color": "black"},
            )
    return fig
