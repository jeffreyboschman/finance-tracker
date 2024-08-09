import pandas as pd
from dotenv import load_dotenv

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import finance_tracker.graphs.utils as graph_utils
from finance_tracker.connectors.notion_api import get_database
from finance_tracker.connectors.notion_to_pandas import get_pandas_df


def graph_business_related_expense_vs_revenue_totals(df: pd.DataFrame, write: bool=False):
    df = df.copy()
    df = df[(df['business_related'] == "Business-Related")]
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.to_period('M').astype(str)

    # Separate data for revenue and expense
    revenue_df = df[df['cash_flow_type'] == 'Revenue']
    # revenue_df['pattern'] = 'One'

    expense_df = df[df['cash_flow_type'] == 'Expense']
    # expense_df['pattern'] = 'One'

    transfer_to_savings_df = df[df['cash_flow_type'] == 'Transfer to Savings']
    transfer_to_savings_df['cash_flow_type'] = 'Expense'
    # transfer_to_savings_df['pattern'] = 'Two'

    # Create a combined DataFrame for plotting
    combined_df = pd.concat([revenue_df, expense_df, transfer_to_savings_df])

    # Plot using Plotly Express
    fig = px.bar(combined_df, x='month_year', y='amount', color='cash_flow_type',
                 color_discrete_map=graph_utils.CASH_FLOW_COLOR_MAP,  
                 title='Business-Related Expense vs Revenue (Monthly Totals)',
                 hover_data={'name': True, 'date': True, 'amount': True, 'month_year': False, 'cash_flow_type': False},
                 category_orders={'month_year': sorted(df['month_year'].unique())},
                 barmode="group")

    fig.update_xaxes(type='category')
    fig.update_layout(xaxis_tickangle=-45)
    
    if write:
        fig.write_html('chart.html')
    else:
        fig.show()


if __name__ == "__main__":
    load_dotenv()
    notion_db = get_database()
    df = get_pandas_df(notion_db)
    graph_business_related_expense_vs_revenue_totals(df, write=False)