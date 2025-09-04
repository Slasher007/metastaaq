# -*- coding: utf-8 -*-
"""
Function to calculate expected monthly power consumption.
"""


def get_expected_monthly_power_cons(electrolyser_power: float, expected_monthly_hours: dict) -> dict:
    """
    Calculate expected monthly power consumption in MWh.

    Parameters:
        electrolyser_power (float): Power of the electrolyser in MW.
        expected_monthly_hours (dict): Expected operating hours per month.

    Returns:
        dict: Expected energy consumption per month in MWh.
    """
    expected_power_cons = {
        month: round(electrolyser_power * hours, 2)
        for month, hours in expected_monthly_hours.items()
    }
    return expected_power_cons
