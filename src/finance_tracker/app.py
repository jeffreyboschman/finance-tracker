import logging
from typing import Callable

import pandas as pd
from flask import Flask, send_file

from finance_tracker.connectors.notion_to_pandas import get_full_df
from finance_tracker.graphs.bus_expense_vs_revenue_totals import (
    graph_business_related_expense_vs_revenue_totals,
)
from finance_tracker.graphs.bus_expense_vs_revenue_waterfall import (
    graph_business_related_expense_vs_revenue_waterfall,
)
from finance_tracker.graphs.bus_transfer_to_savings_totals import (
    graph_business_related_transfer_to_savings_totals,
)

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


def generate_and_serve_chart(
    chart_func: Callable[[pd.DataFrame, bool, str], None], filename: str
) -> send_file:
    """Generates a chart using the provided function and serves it as an HTML file.

    This function retrieves the full DataFrame, generates a chart by invoking the specified
    chart function, and then serves the chart as an HTML file.

    Args:
        chart_func (Callable[[pd.DataFrame, bool, str], None]): The function to generate the chart.
        filename (str): The name of the HTML file to save and serve the chart.

    Returns:
        Response: The Flask response object that serves the HTML file.
    """
    logging.info("Generating chart: %s", filename)

    full_df = get_full_df()
    chart_func(full_df, write=True, chart_filename=filename)
    logging.info("Serving chart: %s", filename)
    try:
        return send_file(filename)
    except FileNotFoundError:
        return "File not found", 404


@app.route("/graphs/expense_vs_revenue_totals")
def serve_business_related_expense_vs_revenue_totals() -> send_file:
    """Serves the business-related expense vs. revenue totals chart.

    This route generates the business-related expense vs. revenue totals chart and serves it
    as an HTML file.

    Returns:
        Response: The Flask response object that serves the HTML file.
    """
    return generate_and_serve_chart(
        graph_business_related_expense_vs_revenue_totals,
        "expense_vs_revenue_totals.html",
    )


@app.route("/graphs/expense_vs_revenue_waterfall")
def serve_business_related_expense_vs_revenue_waterfall():
    """Serves the business-related expense vs. revenue vs. savings waterfall chart.

    This route generates the business-related expense vs. revenue vs. savings waterfall chart
    and serves it as an HTML file.

    Returns:
        Response: The Flask response object that serves the HTML file.
    """
    return generate_and_serve_chart(
        graph_business_related_expense_vs_revenue_waterfall,
        "expense_vs_revenue_waterfall.html",
    )


@app.route("/graphs/transfer_to_savings_totals")
def serve_business_related_transfer_to_savings_totals():
    """Serves the business-related transfer to savings totals chart.

    This route generates the business-related transfer to savings totals chart and serves it
    as an HTML file.

    Returns:
        Response: The Flask response object that serves the HTML file.
    """
    return generate_and_serve_chart(
        graph_business_related_transfer_to_savings_totals,
        "transfer_to_savings_totals.html",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
