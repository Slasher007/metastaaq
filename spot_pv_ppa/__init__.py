# -*- coding: utf-8 -*-
"""
MetaStaaq Spot PV PPA Analysis Package

This package contains functions for analyzing electricity spot prices,
PV energy production, and PPA scenarios for electrolyser operations.
"""

from calculate_max_hours import calculate_max_hours
from display_table import display_table
from get_required_hours_per_month import get_required_hours_per_month
from get_expected_monthly_power_cons import get_expected_monthly_power_cons
from calculate_percentage_difference import calculate_percentage_difference
from plot_chart import plot_chart
from plot_table_as_image import plot_table_as_image
from save_fig_as_png import save_fig_as_png
from run_simulation import run_simulation

__all__ = [
    'calculate_max_hours',
    'display_table',
    'get_required_hours_per_month',
    'get_expected_monthly_power_cons',
    'calculate_percentage_difference',
    'plot_chart',
    'plot_table_as_image',
    'save_fig_as_png',
    'run_simulation'
]
