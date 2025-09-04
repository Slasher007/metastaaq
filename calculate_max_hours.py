# -*- coding: utf-8 -*-
"""
Function to calculate maximum hours that can be purchased each month
while keeping the average price below or equal to the target price.
"""

import pandas as pd
import calendar


def calculate_max_hours(df, target_price=15):
    """
    Calculate the maximum number of hours that can be purchased each month
    while keeping the average price below or equal to the target price

    Parameters:
        df (pd.DataFrame): DataFrame containing electricity price data with 'Date', 'Heure', and 'Prix' columns
        target_price (float): Target price (€/MWh), default is 15

    Returns:
        dict: Maximum purchasable hours organized by year and month with string keys (month as full name)
    """
    # Combine 'Date' and 'Heure' to create 'timestamp' and convert to datetime
    df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Heure'].astype(str) + ':00:00')
    df['year'] = df['timestamp'].dt.year
    df['month'] = df['timestamp'].dt.month

    # Rename 'Prix' to 'price' for consistency with the original logic
    df = df.rename(columns={'Prix': 'price'})

    # Group by year and month
    result = {}
    for (year, month), group in df.groupby(['year', 'month']):
        prices = group['price'].values
        sorted_prices = sorted(prices)  # Sort prices in ascending order

        total_price = 0.0
        max_hours = 0

        for i, price in enumerate(sorted_prices, 1):
            total_price += price
            avg_price = total_price / i
            if avg_price <= target_price:
                max_hours = i
            else:
                break  # Stop once target price is exceeded
        
        if max_hours == 0:
          max_hours = None
        # Create nested dictionary structure with string keys (month as full name)
        year_str = str(year)
        month_name = calendar.month_name[month]
        if year_str not in result:
            result[year_str] = {}
        result[year_str][month_name] = max_hours

    return result
