import create_graphs
from dotenv import load_dotenv
from flask import Flask, send_file
from main import get_database, get_pandas_df

app = Flask(__name__)


@app.route("/chart")
def serve_chart():
    # Generate the chart before serving
    load_dotenv()
    notion_db = get_database()
    df = get_pandas_df(notion_db)
    create_graphs.graph_business_related_expense_vs_revenue_totals(df, write=True)
    return send_file("chart.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
