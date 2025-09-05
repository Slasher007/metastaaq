# -*- coding: utf-8 -*-
"""
Function to calculate percentage difference between actual and expected values.
"""

import pandas as pd


def calculate_percentage_difference(df_actual: pd.DataFrame, expected_values: dict) -> pd.DataFrame:
    """
    Calculate percentage of actual hours vs expected hours (0 to 100%).
    
    Parameters:
        df_actual (pd.DataFrame): DataFrame with actual values
        expected_values (dict): Dictionary with expected values per month
        
    Returns:
        pd.DataFrame: DataFrame with percentage differences
    """
    df_percent = df_actual.copy()
    for month in df_actual.columns:
        expected = expected_values[month]
        if expected == 0:
            # If expected is 0, set percentage to 0 (or None for null values)
            df_percent[month] = df_actual[month].apply(
                lambda x: 0.0 if pd.notnull(x) else None
            )
        else:
            df_percent[month] = df_actual[month].apply(
                lambda x: round((x / expected) * 100, 2) if pd.notnull(x) else None
            )
    return df_percent
