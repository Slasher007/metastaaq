# -*- coding: utf-8 -*-
"""
Main simulation function that orchestrates the entire analysis workflow.
"""

import pandas as pd
import matplotlib.pyplot as plt
import calendar

from get_required_hours_per_month import get_required_hours_per_month
from get_expected_monthly_power_cons import get_expected_monthly_power_cons
from calculate_max_hours import calculate_max_hours
from display_table import display_table
from calculate_percentage_difference import calculate_percentage_difference
from plot_chart import plot_chart
from plot_table_as_image import plot_table_as_image


def run_simulation(data_content, target_price, service_ratio, electrolyser_power, ch4_kg_per_day, ppa_price=80):
    """
    Run the complete simulation for a given target price.
    
    Parameters:
        data_content (pd.DataFrame): Price data
        target_price (float): Target price in €/MWh
        service_ratio (float): Service ratio (0-1)
        electrolyser_power (float): Power rating in MW
        ch4_kg_per_day (float): CH4 production rate in kg/day
        ppa_price (float): PPA price in €/MWh, default is 80
    """
    # Get expected monthly Hours
    expected_monthly_hours = get_required_hours_per_month(service_ratio)
    expected_monthly_power = get_expected_monthly_power_cons(electrolyser_power, expected_monthly_hours)
    result, extended_info = calculate_max_hours(data_content, target_price, ppa_price, return_extended_info=True)
    df_result = display_table(result)

    # Calculate Available Hours difference
    df_hour_diff = calculate_percentage_difference(df_result, expected_monthly_hours)

    # Display power consumption table
    df_power_consumption = df_result * electrolyser_power

    # Calculate Available Power difference
    df_power_diff = calculate_percentage_difference(df_power_consumption, expected_monthly_power)

    # Display table of Available Hours
    table_title = f'Maximum Available Hours with {service_ratio*100}% service ratio and average target price {target_price}€/MWH - {electrolyser_power} MW'
    plot_table_as_image(df_result, table_title)

    # Display chart of Available Hours and Power Coverage with left dual y-axis
    title = f'Maximum Available Hours {service_ratio*100}% service ratio and average target price {target_price}€/MWH'
    plot_chart(df_result, target_price, title, electrolyser_power, 'Available Hours', df_power_diff=df_power_diff, ch4_kg_per_day=ch4_kg_per_day, extended_info=extended_info, ppa_price=ppa_price)

    # Monthly PV energy outputs in kWh - Define inside or pass as argument if varies
    pv_energy_kwh = {
        "January": 41329.5, "February": 62809.8, "March": 100499.8,
        "April": 128700.4, "May": 132130.6, "June": 133177.3,
        "July": 136106.0, "August": 127150.4, "September": 112236.2,
        "October": 79940.3, "November": 48793.6, "December": 40402.6
    }
    pv_energy_mwh = {month: kwh / 1000 for month, kwh in pv_energy_kwh.items()}

    # Daily demand in MWh
    daily_demand_mwh = 120

    # Days in each month (non-leap year) - Define inside or pass as argument if varies
    days_in_month = {
        "January": 31, "February": 28, "March": 31, "April": 30,
        "May": 31, "June": 30, "July": 31, "August": 31,
        "September": 30, "October": 31, "November": 30, "December": 31
    }
    monthly_demand_mwh = {month: daily_demand_mwh * days for month, days in days_in_month.items()}

    # Get the monthly power consumption based on available hours from the simulation
    # Take the average across years for each month
    monthly_available_power = df_power_consumption.mean().to_dict()

    # Calculate maximum possible power consumption for each month based on service ratio
    max_monthly_consumption = {
        month: electrolyser_power * 24 * service_ratio * days_in_month[month]
        for month in days_in_month
    }

    # Create a DataFrame for plotting with the new structure
    df_plot_data = pd.DataFrame({
        'Maximum Consumption (MWh)': pd.Series(max_monthly_consumption),
        'PV-covered (MWh)': pd.Series(pv_energy_mwh),
        'Spot Target (MWh)': pd.Series(monthly_available_power)
    })

    # Calculate the remaining unmet demand
    df_plot_data['Remaining Unmet Demand (MWh)'] = df_plot_data['Maximum Consumption (MWh)'] - df_plot_data['PV-covered (MWh)'] - df_plot_data['Spot Target (MWh)']
    # Ensure remaining unmet demand is not negative due to potential floating point issues or if available power exceeds demand/max consumption in some cases
    df_plot_data['Remaining Unmet Demand (MWh)'] = df_plot_data['Remaining Unmet Demand (MWh)'].clip(lower=0)

    # Ensure the order of months is correct for plotting
    month_order = list(calendar.month_name)[1:]
    df_plot_data = df_plot_data.reindex(month_order)

    # Plotting the stacked bar chart with the new structure
    # We will plot PV-covered, Available Power, and Remaining Unmet Demand
    fig, ax1 = plt.subplots(figsize=(12, 6))  # Create figure and primary axes

    bars = df_plot_data[['PV-covered (MWh)', 'Spot Target (MWh)', 'Remaining Unmet Demand (MWh)']].plot(
        kind='bar', stacked=True, ax=ax1, color=['blue', 'green', 'red']
    )

    # Add percentage labels to the bars
    for container in bars.containers:
        for bar in container:
            height = bar.get_height()
            # Calculate the percentage of the total height
            total_height = sum([b.get_height() for b in container.__class__(bar.axes.patches) if b.get_x() == bar.get_x()])
            percentage = (height / total_height) * 100 if total_height > 0 else 0
            ax1.text(bar.get_x() + bar.get_width()/2.,
                     bar.get_y() + height/2.,
                     f'{percentage:.1f}%',
                     ha='center', va='center',
                     color='white', fontsize=8, weight='bold')

    plt.title(f'Monthly Energy Coverage (Target Price: {target_price}€/MWh)')  # Update title
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Energy (MWh)')
    ax1.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()
