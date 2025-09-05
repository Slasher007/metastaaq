# -*- coding: utf-8 -*-
"""
Function to plot charts with multiple y-axes for different metrics.
"""

import matplotlib.pyplot as plt
import pandas as pd


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
    
    # Handle extended hours visualization if extended_info is provided
    if extended_info is not None:
        # Create separate dataframes for base and extended hours
        base_hours_data = pd.DataFrame(index=df_plot.index, columns=df_plot.columns, dtype=float)
        extended_hours_data = pd.DataFrame(index=df_plot.index, columns=df_plot.columns, dtype=float)
        
        for year in df_plot.columns:
            for month in df_plot.index:
                if str(year) in extended_info and month in extended_info[str(year)]:
                    info = extended_info[str(year)][month]
                    base_hours_data.loc[month, year] = info['base_hours']
                    extended_hours_data.loc[month, year] = info['extended_hours']
                else:
                    base_hours_data.loc[month, year] = df_plot.loc[month, year] if pd.notna(df_plot.loc[month, year]) else 0
                    extended_hours_data.loc[month, year] = 0
        
        # Fill NaN values with 0
        base_hours_data = base_hours_data.fillna(0)
        extended_hours_data = extended_hours_data.fillna(0)
        
        # Create manual bar chart to properly handle stacked visualization
        x_pos = range(len(df_plot.index))
        width = 0.8 / len(df_plot.columns)  # Width of bars
        
        # Colors for different years
        colors = plt.cm.tab10(range(len(df_plot.columns)))
        
        # Plot bars for each year
        for i, year in enumerate(df_plot.columns):
            x_offset = [x + width * (i - len(df_plot.columns)/2 + 0.5) for x in x_pos]
            
            # Base hours
            base_values = base_hours_data[year].values
            ax1.bar(x_offset, base_values, width, 
                   label=f'{year}', color=colors[i], alpha=0.8)
            
            # Extended hours (stacked on top)
            extended_values = extended_hours_data[year].values
            ax1.bar(x_offset, extended_values, width, 
                   bottom=base_values, color='gray', alpha=0.6)
        
        # Set x-axis labels
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(df_plot.index)
        
        # Add legend entry for extended hours using Rectangle patch for better alpha rendering
        from matplotlib.patches import Rectangle
        extended_patch = Rectangle((0, 0), 1, 1, facecolor='gray', alpha=0.6, label='Extended Hours (avg < PPA)')
        
        # Get current handles and labels, then add the extended hours patch
        handles, labels = ax1.get_legend_handles_labels()
        handles.append(extended_patch)
        labels.append('Extended Hours (avg < PPA)')
    else:
        # Original plotting without extended hours
        df_plot.plot(kind='bar', ax=ax1, legend=True)

    # Plot monthly average line on ax1
    ax1.plot(
        range(len(monthly_avg)),
        monthly_avg.values,
        color='black',
        linestyle='--',
        marker='o',
        label='Monthly Average'
    )

    # Labels and formatting for the primary y-axis (Available Hours)
    ax1.set_xlabel('Month')
    ax1.set_ylabel(y_label)
    if extended_info is not None:
        ax1.set_title(f"{title} - {power} MW (Extended to PPA {ppa_price}€/MWh)")
        # Use custom legend with extended hours patch
        ax1.legend(handles=handles, labels=labels, loc='upper left')
    else:
        ax1.set_title(f"{title} - {power} MW")
        ax1.legend(loc='upper left')
    ax1.tick_params(axis='x', rotation=45)

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
