# -*- coding: utf-8 -*-
"""
Function to calculate required hours per month based on service ratio.
"""


def get_required_hours_per_month(service_ratio: float) -> dict:
    """
    Returns a dictionary with available hours per month based on a given service ratio.

    Parameters:
        service_ratio (float): Availability ratio (e.g., 0.98 for 98%)

    Returns:
        dict: Keys are month names, values are available hours (float)
    """
    days_per_month = {
        "January": 31,
        "February": 28,  # Non-leap year
        "March": 31,
        "April": 30,
        "May": 31,
        "June": 30,
        "July": 31,
        "August": 31,
        "September": 30,
        "October": 31,
        "November": 30,
        "December": 31
    }

    required_hours = {
        month: round(days * 24 * service_ratio, 0)
        for month, days in days_per_month.items()
    }

    return required_hours
