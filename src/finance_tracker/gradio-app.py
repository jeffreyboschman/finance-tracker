import asyncio
import logging
import os

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

from finance_tracker.connectors.notion_to_pandas import get_finance_tracker_df
from finance_tracker.graphs.bus_expense_vs_revenue_totals import (
    graph_business_related_expense_vs_revenue_totals,
)
from finance_tracker.graphs.bus_expense_vs_revenue_waterfall import (
    graph_business_related_expense_vs_revenue_waterfall,
)
from finance_tracker.graphs.bus_transfer_to_savings_totals import (
    graph_business_related_transfer_to_savings_totals,
)
from finance_tracker.graphs.nonbus_subcategory_totals import (
    graph_nonbusiness_related_subcategory_percentages,
    graph_nonbusiness_related_subcategory_totals,
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


def display_expense_vs_revenue_totals() -> go.Figure:
    """Displays the business-related expense vs. revenue totals chart."""
    return generate_chart(graph_business_related_expense_vs_revenue_totals)


def display_expense_vs_revenue_waterfall() -> go.Figure:
    """Displays the business-related expense vs. revenue vs. savings waterfall chart."""
    return generate_chart(graph_business_related_expense_vs_revenue_waterfall)


def display_transfer_to_savings_totals() -> go.Figure:
    """Displays the business-related transfer to savings totals chart."""
    return generate_chart(graph_business_related_transfer_to_savings_totals)


def display_nonbusiness_expense_categories() -> go.Figure:
    """Displays the business-related transfer to savings totals chart."""
    return generate_chart(graph_nonbusiness_related_subcategory_totals)


def display_nonbusiness_expense_category_percentages() -> go.Figure:
    """Displays the business-related transfer to savings percentages chart."""
    return generate_chart(graph_nonbusiness_related_subcategory_percentages)


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

        gr.Markdown("### Business-related Expense vs. Revenue Totals")
        expense_vs_revenue_totals_btn = gr.Button("Show Chart")
        expense_vs_revenue_totals_output = gr.Plot()
        expense_vs_revenue_totals_btn.click(
            display_expense_vs_revenue_totals, outputs=expense_vs_revenue_totals_output
        )

        gr.Markdown("### Business-related Expense vs. Revenue Waterfall")
        expense_vs_revenue_waterfall_btn = gr.Button("Show Chart")
        expense_vs_revenue_waterfall_output = gr.Plot()
        expense_vs_revenue_waterfall_btn.click(
            display_expense_vs_revenue_waterfall,
            outputs=expense_vs_revenue_waterfall_output,
        )

        gr.Markdown("### Business-related Transfer to Savings Totals")
        transfer_to_savings_totals_btn = gr.Button("Show Chart")
        transfer_to_savings_totals_output = gr.Plot()
        transfer_to_savings_totals_btn.click(
            display_transfer_to_savings_totals,
            outputs=transfer_to_savings_totals_output,
        )

        gr.Markdown("### Non-Business-related Expense Category Totals")
        nonbusiness_expense_categories_btn = gr.Button("Show Chart")
        nonbusiness_expense_categories_output = gr.Plot()
        nonbusiness_expense_categories_btn.click(
            display_nonbusiness_expense_categories,
            outputs=nonbusiness_expense_categories_output,
        )

        gr.Markdown("### Non-Business-related Expense Category Percentages")
        nonbusiness_expense_category_percentages_btn = gr.Button("Show Chart")
        nonbusiness_expense_category_percentages_output = gr.Plot()
        nonbusiness_expense_category_percentages_btn.click(
            display_nonbusiness_expense_category_percentages,
            outputs=nonbusiness_expense_category_percentages_output,
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
