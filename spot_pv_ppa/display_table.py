# -*- coding: utf-8 -*-
"""
Function to display results as a formatted table.
"""

import pandas as pd
import calendar


def display_table(result):
    """
    Convert the nested dictionary to a pandas DataFrame and format it properly.
    
    Parameters:
        result (dict): Nested dictionary with years and months data
        
    Returns:
        pd.DataFrame: Formatted DataFrame with years as index and months as columns
    """
    # Convert the nested dictionary to a pandas DataFrame
    df_result = pd.DataFrame.from_dict(result, orient='index')

    # Rename the index to 'Year' and the columns to 'Month'
    df_result.index.name = 'Year'
    df_result.columns.name = 'Month'

    # Sort the columns by month order
    month_order = list(calendar.month_name)[1:]  # Get month names from calendar module, excluding empty string at index 0
    df_result = df_result[month_order]

    return df_result
