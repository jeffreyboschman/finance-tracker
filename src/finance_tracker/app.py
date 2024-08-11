from flask import Flask, send_file

from finance_tracker.connectors.notion_to_pandas import get_full_df
from finance_tracker.graphs.bus_expense_vs_revenue_totals import (
    graph_business_related_expense_vs_revenue_totals,
)

app = Flask(__name__)


@app.route("/chart")
def serve_chart():
    # Generate the chart before serving
    full_df = get_full_df()
    graph_business_related_expense_vs_revenue_totals(full_df, write=True)
    return send_file("chart.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
