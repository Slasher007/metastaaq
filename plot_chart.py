# -*- coding: utf-8 -*-
"""
Function to plot charts with multiple y-axes for different metrics.
"""

import matplotlib.pyplot as plt


def plot_chart(df_result, target_price, title, power, y_label, df_power_diff=None, ch4_kg_per_day=None):
    """
    Plot chart with multiple y-axes showing available hours, power consumption, and CH4 production.
    
    Parameters:
        df_result (pd.DataFrame): DataFrame with results to plot
        target_price (float): Target price for the chart title
        title (str): Chart title
        power (float): Power rating in MW
        y_label (str): Label for primary y-axis
        df_power_diff (pd.DataFrame, optional): DataFrame with power differences
        ch4_kg_per_day (float, optional): CH4 production rate in kg/day
    """
    # Transpose for plotting (months on x-axis)
    df_plot = df_result.T
    # Calculate average per month
    monthly_avg = df_plot.mean(axis=1)

    # Create the main axis and bar plot
    fig, ax1 = plt.subplots(figsize=(12, 6))
    df_plot.plot(kind='bar', ax=ax1, legend=True)

    # Plot monthly average line on ax1
    ax1.plot(
        monthly_avg.index,
        monthly_avg.values,
        color='black',
        linestyle='--',
        marker='o',
        label='Monthly Average'
    )

    # Labels and formatting for the primary y-axis (Available Hours)
    ax1.set_xlabel('Month')
    ax1.set_ylabel(y_label)
    ax1.set_title(f"{title} - {power} MW")
    ax1.tick_params(axis='x', rotation=45)
    ax1.legend(loc='upper left')

    # ---------------------
    # First Right Y-axis: Power Consumption
    # ---------------------
    #ax2 = ax1.twinx()
    #max_power_consumption = power * 24  # MWh/day
    #power_ticks = [max_power_consumption * i / 5 for i in range(6)]  # 6 divisions
    #ax2.set_ylabel('Power Consumption (MWh/day)', color='blue')
    #ax2.set_ylim(0, max_power_consumption)
    #ax2.set_yticks(power_ticks)
    #ax2.tick_params(axis='y', labelcolor='blue')
    #ax2.grid(False)

    # ---------------------
    # Third Y-axis: CH₄ Production
    # ---------------------
    if ch4_kg_per_day is not None:
        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))  # Offset to avoid overlap
        max_ch4_production = ch4_kg_per_day  # Since this is already kg/day
        ch4_ticks = [max_ch4_production * i / 5 for i in range(6)]  # 6 divisions
        ax3.set_ylabel('CH₄ Production (kg/day)', color='green')
        ax3.set_ylim(0, max_ch4_production)
        ax3.set_yticks(ch4_ticks)
        ax3.tick_params(axis='y', colors='green')

        # Make tick labels green
        for tick_label in ax3.get_yticklabels():
            tick_label.set_color('green')

    # Final layout
    plt.tight_layout()
    plt.show()
