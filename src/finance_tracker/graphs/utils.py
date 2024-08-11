import calendar

CASH_FLOW_COLOR_MAP = {
    "Revenue": "#4DAB9A",
    "Expense": "#FF7369",
    "Transfer to Savings": "#FFDC49",
    "Bank Transfer Out": "#FFA344",
    "Bank Transfer In": "#529CCA",
}
# Colors from: https://optemization.notion.site/b58409d4a92444368cbad42b60d9ea55?v=8de8c56bd44f4239ab7cd145c62d35c3

CASH_FLOW_PATTERN_MAP = {
    "Revenue": "",
    "Expense": "#FF7369",
    "Transfer to Savings": "#FFDC49",
    "Bank Transfer Out": "#FFA344",
    "Bank Transfer In": "#529CCA",
}


def get_days_in_month(year, month):
    # Get the number of days in the given month
    num_days = calendar.monthrange(year, month)[1]
    # Generate a list of all the days in the month
    days_in_month = [day for day in range(1, num_days + 1)]
    return days_in_month
