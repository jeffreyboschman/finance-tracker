import asyncio
import logging
import os

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

from finance_tracker.connectors.notion_to_pandas import get_finance_tracker_df
from finance_tracker.graphs.revenue_vs_expense_totals import (
    graph_business_revenue_vs_expense_and_tax_totals,
    graph_personal_revenue_vs_expense_and_saving_totals,
)
from finance_tracker.graphs.subcategory import (
    graph_business_expenses_and_taxes_by_subcategory,
    graph_business_expenses_by_subcategory,
    graph_business_revenue_by_subcategory,
    graph_personal_expenses_and_savings_by_subcategory,
    graph_personal_expenses_by_subcategory,
    graph_personal_revenue_by_subcategory,
)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

cached_df = None


def get_or_update_data() -> pd.DataFrame:
    """Fetches and returns the global cached DataFrame.

    If the cached DataFrame is None, it updates the cache by fetching the data.

    Returns:
        pd.DataFrame: The cached or newly fetched DataFrame.
    """
    global cached_df
    if cached_df is None:
        _logger.info("Data not loaded. Fetching data from Notion...")
        cached_df = get_finance_tracker_df()
        _logger.info("Data fetched and cached successfully.")
    return cached_df


def update_cached_data() -> str:
    """Forcibly updates the global cached DataFrame.

    Returns:
        str: A message indicating that the data has been updated.
    """
    global cached_df
    _logger.info("Forcing data update from Notion...")
    cached_df = get_finance_tracker_df()
    _logger.info("Data updated successfully.")
    return "Data updated successfully."


def generate_chart(chart_func) -> go.Figure:
    """Generates a chart using the provided function and returns a Plotly
    Figure object representing the chart.

    Args:
        chart_func (Callable[[pd.DataFrame], go.Figure]): The function to generate
            the chart.

    Returns:
        go.Figure: A Plotly Figure object representing the bar chart.
    """
    df = get_or_update_data()
    _logger.info("Generating chart...")
    fig = chart_func(df)
    _logger.info("Chart generated successfully.")
    return fig


# Revenue vs Expense totals


def display_business_revenue_vs_expense_and_tax_totals() -> go.Figure:
    """Displays the business expense vs. revenue totals chart."""
    return generate_chart(graph_business_revenue_vs_expense_and_tax_totals)


def display_personal_revenue_vs_expense_and_saving_totals() -> go.Figure:
    """Displays the personal expense vs. revenue totals chart."""
    return generate_chart(graph_personal_revenue_vs_expense_and_saving_totals)


# Business by category


def display_business_revenue_by_subcategory() -> go.Figure:
    return generate_chart(graph_business_revenue_by_subcategory)


def display_business_expenses_by_subcategory() -> go.Figure:
    return generate_chart(graph_business_expenses_by_subcategory)


def display_business_expenses_and_taxes_by_subcategory() -> go.Figure:
    return generate_chart(graph_business_expenses_and_taxes_by_subcategory)


# Personal by category


def display_personal_revenue_by_subcategory() -> go.Figure:
    return generate_chart(graph_personal_revenue_by_subcategory)


def display_personal_expenses_by_subcategory() -> go.Figure:
    return generate_chart(graph_personal_expenses_by_subcategory)


def display_personal_expenses_and_savings_by_subcategory() -> go.Figure:
    return generate_chart(graph_personal_expenses_and_savings_by_subcategory)


async def main():
    load_dotenv()

    gradio_server_name = os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0")
    gradio_server_port = os.environ.get("GRADIO_SERVER_PORT", "7860")
    gradio_user_password = os.environ.get("GRADIO_PASSWORD")

    auth_fn = (
        (lambda _username, password: password == gradio_user_password)
        if gradio_user_password is not None
        else None
    )

    # Mapping of chart names to functions
    chart_functions = {
        "Business Revenue vs Expense (and Tax) - Totals": display_business_revenue_vs_expense_and_tax_totals,
        "Personal Revenue vs Expense (and Saving) - Totals": display_personal_revenue_vs_expense_and_saving_totals,
        "Business Revenue - by Category": display_business_revenue_by_subcategory,
        "Business Expenses - by Category": display_business_expenses_by_subcategory,
        "Business Expenses (and Taxes) - by Category": display_business_expenses_and_taxes_by_subcategory,
        "Personal Revenue - by Category": display_personal_revenue_by_subcategory,
        "Personal Expenses - by Category": display_personal_expenses_by_subcategory,
        "Personal Expenses (and Savings) - by Category": display_personal_expenses_and_savings_by_subcategory,
    }

    # Set up Gradio interface
    with gr.Blocks(
        theme=gr.themes.Soft(),
        analytics_enabled=False,
        css="footer{display:none !important}",
    ) as demo:
        gr.Markdown("# Financial Graphs Dashboard")

        gr.Markdown("### Update Data")
        update_data_btn = gr.Button("Update Data")
        update_data_output = gr.Textbox(label="Update Status")
        update_data_btn.click(update_cached_data, outputs=update_data_output)

        gr.Markdown("### Select Charts to Display")
        chart_dropdown1 = gr.Dropdown(
            choices=list(chart_functions.keys()),
            label="Select First Chart",
            value=list(chart_functions.keys())[0],
        )
        chart_dropdown2 = gr.Dropdown(
            choices=list(chart_functions.keys()),
            label="Select Second Chart",
            value=list(chart_functions.keys())[1],
        )
        display_chart_btn = gr.Button("Display Charts")
        chart_output1 = gr.Plot()
        chart_output2 = gr.Plot()

        def display_selected_charts(chart_name1, chart_name2):
            chart_func1 = chart_functions[chart_name1]
            chart_func2 = chart_functions[chart_name2]

            return chart_func1(), chart_func2()

        display_chart_btn.click(
            display_selected_charts,
            inputs=[chart_dropdown1, chart_dropdown2],
            outputs=[chart_output1, chart_output2],
        )

    demo.queue()
    demo.launch(
        server_name=gradio_server_name,
        server_port=int(gradio_server_port),
        share=False,
        auth=auth_fn,
    )


if __name__ == "__main__":
    asyncio.run(main())
