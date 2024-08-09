
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import graph_helpers as graph_helpers


def graph_prestia_cash_flow_in_out_for_month(df, target_month, target_year):
    """
    Generates a bar graph of Prestia cash flow in and out for a specific month and year.

    This function filters the provided DataFrame for the specified month and year, excluding 
    accounts "Sony Bank (Jeff)" and "Sony Bank (Mel)". It then categorizes the data into 
    "Cash Flow In" and "Cash Flow Out" based on the `cash_flow_type` column and plots the 
    results using Plotly.

    Args:
        df (pd.DataFrame): The input DataFrame containing cash flow data with columns 
            ['date', 'account', 'cash_flow_type', 'amount', 'name'].
        target_month (int or str): The target month for filtering data (1-12).
        target_year (int or str): The target year for filtering data (e.g., 2023).

    Returns:
        None: This function displays a Plotly bar graph and does not return any value.

    Raises:
        ValueError: If `target_month` or `target_year` are not valid integers or strings
            that can be converted to integers.
    
    """
    df = df.copy()
    # Filter by account
    df = df[(df['account'] != "Sony Bank (Jeff)") & (df['account'] != "Sony Bank (Mel)") ]
    
    # Filter by date
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df = df[(df['month'] == int(target_month)) & (df['year'] == int(target_year))]
    df = df.sort_values(by='date')


    # Data for Cash Flow In
    revenue_df = df[df['cash_flow_type'] == 'Revenue']
    revenue_df['Cash Flow'] = 'Cash Flow In'
    bank_transfer_in_df = df[df['cash_flow_type'] == 'Bank Transfer In']
    bank_transfer_in_df['Cash Flow'] = 'Cash Flow In'

    # Data for Cash Flow Out
    expense_df = df[df['cash_flow_type'] == 'Expense']
    expense_df['Cash Flow'] = 'Cash Flow Out'
    savings_df = df[df['cash_flow_type'] == 'Transfer to Savings']
    savings_df['Cash Flow'] = 'Cash Flow Out'
    bank_transfer_out_df = df[df['cash_flow_type'] == 'Bank Transfer Out']
    bank_transfer_out_df['Cash Flow'] = 'Cash Flow Out'

    # Create a combined DataFrame for plotting
    combined_df = pd.concat([revenue_df, bank_transfer_in_df, expense_df, savings_df, bank_transfer_out_df])
    
    # Plotting
    fig = px.bar(combined_df, x='Cash Flow', y='amount', color='cash_flow_type',
                 color_discrete_map=graph_helpers.CASH_FLOW_COLOR_MAP,  
                 title=f'Prestia Cash Flow In vs Out ({target_month}-{target_year})',
                 hover_data={'name': True, 'date': True, 'amount': True, 'cash_flow_type': False, "Cash Flow": False})
    fig.update_xaxes(type='category')
    fig.update_layout(xaxis_tickangle=-45)

    fig.show()

def graph_prestia_expense_vs_revenue_totals(df):
    df = df.copy()
    df = df[(df['account'] != "Sony Bank (Jeff)") & (df['account'] != "Sony Bank (Mel)") ]
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    df['month_year'] = df['date'].dt.to_period('M').astype(str)

    # Separate data for revenue and expense
    revenue_df = df[df['expense_vs_revenue'] == 'Revenue']
    revenue_df.loc[:, 'Group'] = 'Revenue'

    expense_df = df[df['expense_vs_revenue'] == 'Expense']
    expense_df.loc[:, 'Group'] = 'Expense'

    savings_df = df[df['expense_vs_revenue'] == 'Transfer to Savings']
    savings_df.loc[:, 'Group'] = 'Expense'

    # Create a combined DataFrame for plotting
    combined_df = pd.concat([revenue_df, expense_df, savings_df])
    print(combined_df.head(100))

    # Plot using Plotly Express
    fig = px.bar(combined_df, x='month_year', y='amount', color='expense_vs_revenue',
                 color_discrete_map=graph_helpers.CASH_FLOW_COLOR_MAP,  
                 title='Business-Related Expense vs Revenue (Monthly Totals)',
                 hover_data={'name': True, 'date': True, 'amount': True, 'month_year': False, 'expense_vs_revenue': False, "Group": False},
                 category_orders={'month_year': sorted(df['month_year'].unique())},
                 barmode="group")
    
    # Update the figure to reflect the changes

    fig.update_xaxes(type='category')
    fig.update_layout(xaxis_tickangle=-45)

    fig.show()



# def graph_business_related_expense_vs_revenue_totals(df):
#     df = df.copy()
#     df = df[(df['business_related'] == "Business-Related")]
#     df['date'] = pd.to_datetime(df['date'])
#     df['month_year'] = df['date'].dt.to_period('M').astype(str)

#     # Separate data for revenue, expense, and transfer to savings
#     revenue_df = df[df['cash_flow_type'] == 'Revenue']

#     expense_df = df[df['cash_flow_type'] == 'Expense']
#     transfer_to_savings_df = df[df['cash_flow_type'] == 'Transfer to Savings']
    
#     combined_df = pd.concat([revenue_df, expense_df, transfer_to_savings_df])

#     # Adjust the combined DataFrame to differentiate stacking and grouping
#     combined_df['stack_group'] = combined_df['cash_flow_type'].apply(
#         lambda x: 'Expenses and Transfers' if x in ['Expense', 'Transfer to Savings'] else x
#     )


#     # Plot using Plotly Express
#     fig = px.bar(combined_df, x='month_year', y='amount', color='cash_flow_type',
#                  color_discrete_map=graph_helpers.CASH_FLOW_COLOR_MAP,
#                  title='Business-Related Expense vs Revenue (Monthly Totals)',
#                  hover_data={'name': True, 'date': True, 'amount': True, 'month_year': False, 'cash_flow_type': False},
#                  category_orders={'month_year': sorted(df['month_year'].unique())},
#                  barmode='group')

#     # Update layout to separate and stack bars
#     fig.update_layout(barmode='stack', xaxis_tickangle=-45)
#     fig.for_each_trace(
#         lambda trace: trace.update(
#             offsetgroup=trace.name if trace.name != 'Expense' else 'Expenses and Transfers',
#             stackgroup=trace.name if trace.name in ['Expense', 'Transfer to Savings'] else None,
#             showlegend=trace.name in ['Expense', 'Transfer to Savings', 'Revenue']
#         )
#     )

#     fig.show()


def graph_business_related_transfer_to_savings_totals(df):
    """Good one"""
    df = df.copy()
    df = df[(df['business_related'] == "Business-Related")]
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.to_period('M').astype(str)

    savings_df = df[df['cash_flow_type'] == 'Transfer to Savings']

    total_accumulated = savings_df['amount'].sum()

    # Plot using Plotly Express
    fig = px.bar(savings_df, x='month_year', y='amount', color='cash_flow_type',
                 color_discrete_map=graph_helpers.CASH_FLOW_COLOR_MAP,  
                 title='Business-Related Tranfer to Savings (Monthly Totals)',
                 hover_data={'name': True, 'date': True, 'amount': True, 'month_year': False, 'cash_flow_type': False},
                 category_orders={'month_year': sorted(df['month_year'].unique())},
                 barmode="group")
    
    fig.add_annotation(
        text=f"Total Accumulated: ¥{total_accumulated:,.2f}",
        xref="paper", yref="paper",
        x=1, y=1, showarrow=False,
        font=dict(size=12, color="black"),
        bgcolor="white", bordercolor="black", borderwidth=1
    )

    fig.update_xaxes(type='category')
    fig.update_layout(xaxis_tickangle=-45)

    fig.show()




def graph_business_related_expense_vs_revenue_vs_savings_waterfall(df, file_path=None):
    """
    Generates a waterfall graph of business-related expenses versus revenues 
    and optionally saves it as an HTML file.

    This function filters the provided DataFrame for business-related transactions and 
    aggregates the data into revenue and expense categories by date. Revenue amounts are 
    halved, and expenses are made negative. The data is then aggregated by date, and a 
    cumulative waterfall chart is generated using Plotly.

    Args:
        df (pd.DataFrame): The input DataFrame containing cash flow data with columns 
            ['date', 'business_related', 'cash_flow_type', 'amount', 'name'].
        file_path (str, optional): The path to save the HTML file. If not provided, 
            the plot will not be saved.

    Returns:
        None: This function displays a Plotly waterfall graph and optionally saves it as an HTML file.

    Raises:
        ValueError: If the 'date' column cannot be converted to datetime format.

    """
    df = df.copy()
    df = df[(df['business_related'] == "Business-Related")]
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    
    # Separate data for revenue and expense and savings
    revenue_df = df[df['cash_flow_type'] == 'Revenue']

    expense_df = df[df['cash_flow_type'] == 'Expense']
    expense_df['amount'] = -1*(expense_df['amount'])

    savings_df = df[df['cash_flow_type'] == 'Transfer to Savings']
    savings_df['amount'] = -1*(savings_df['amount'])    

    # Create a combined DataFrame for plotting
    combined_df = pd.concat([expense_df, savings_df, revenue_df])

    def aggregate_names_amounts(group):
        return ', '.join([f"{name} ({'+' if amount > 0 else ''}{amount})" for name, amount in zip(group['name'], group['amount'])])

    combined_agg_df = combined_df.groupby('date').apply(
        lambda group: pd.Series({
            'amount': group['amount'].sum(),
            'name': aggregate_names_amounts(group)
        })
    ).reset_index()

    combined_agg_df = combined_agg_df.sort_values(by='date')

    fig = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        x=combined_agg_df['date'],
        y=combined_agg_df['amount'],
        measure=['relative'] * len(combined_agg_df),
        textposition='outside',
        text=combined_agg_df['name'],
        hoverinfo='text',
        increasing = {"marker":{"color":'#2CA02C'}},
        decreasing = {"marker":{"color":'#EF553B'}},
    ))

    fig.update_layout(title='Business-Related Expense vs Revenue (Cumulative Waterfall)',
                    xaxis_title='Date',
                    yaxis_title='Amount (¥)',
                    xaxis_tickangle=-45)

    fig.show()

    if file_path:
        pio.write_html(fig, file_path, auto_open=False)


def graph_waterfall(df):
    # WITH WATERFALL
    # Calculate cumulative sum of amounts
    df = df.copy()
    df = df[(df['account'] == "Sony Bank (Mel)") | (df["account"] ==  "Sony Bank (Jeff)")]
    df['date'] = pd.to_datetime(df['date'])

    # df['cumulative_amount'] = df['amount'].cumsum()
    # Separate data for revenue and expense
    revenue_df = df[df['expense_vs_revenue'] == 'Revenue']
    revenue_df['date'] = pd.to_datetime("2024-04-01")
    # revenue_df = revenue_df.groupby('date').agg({'amount': 'sum', 'name': lambda x: ', '.join(x)}).reset_index()

    expense_df = df[df['expense_vs_revenue'] == 'Expense']
    expense_df['amount'] = -1*(expense_df['amount'])
    # expense_df = expense_df.groupby('date').agg({'amount': 'sum', 'name': lambda x: ', '.join(x)}).reset_index()

    # Create a combined DataFrame for plotting
    combined_df = pd.concat([revenue_df, expense_df])
    combined_df = combined_df.groupby('date').agg({'amount': 'sum', 'name': lambda x: ', '.join(x)}).reset_index()
    combined_df = combined_df.sort_values(by='date')

    print(combined_df.head(100))
    # daily_summary = df.groupby('date').agg({'amount': 'sum', 'name': lambda x: ', '.join(x)}).reset_index()
    
    custom_x_range = pd.date_range(start='2024-04-01', end='2024-04-30')  # Custom range of dates

    fig = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        x=combined_df['date'],
        y=combined_df['amount'],
        measure=['relative'] * len(combined_df),
        textposition='outside',
        text=combined_df['name'],
        hoverinfo='text',
    ))

    max_y_value = combined_df['amount'].max()
    last_x_value = combined_df['date'].iloc[-1]
    linear_line = pd.DataFrame({'date': [combined_df['date'].iloc[0], last_x_value], 'amount': [max_y_value, 0]})
    fig.add_trace(go.Scatter(x=linear_line['date'], y=linear_line['amount'], mode='lines', name='Linear Line'))

    fig.update_layout(title='Cumulative Amount Spent over Time',
                    xaxis_title='Date',
                    yaxis_title='Cumulative Amount Spent',
                    xaxis_tickangle=-45,
                    xaxis_range=[custom_x_range[0], custom_x_range[-1]]  # Set x-axis range
)

    # fig.show()
    return fig.to_html(full_html=True)