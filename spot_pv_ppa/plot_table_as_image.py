# -*- coding: utf-8 -*-
"""
Function to plot pandas DataFrame as an image with Excel-like styling.
"""

import matplotlib.pyplot as plt


def plot_table_as_image(df, title):
    """
    Plots a pandas DataFrame as an image using matplotlib with an Excel-like style.

    Parameters:
        df (pd.DataFrame): The DataFrame to plot.
        title (str): The title of the plot.
    """
    fig, ax = plt.subplots(figsize=(12, 4))  # Adjust figsize as needed
    ax.axis('off')  # Hide axes

    # Reset index to include the 'Year' as a column for plotting
    df_reset = df.reset_index()

    # Create the table
    table = ax.table(cellText=df_reset.values, colLabels=df_reset.columns, loc='center')

    # Styling the table to look more like Excel
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)  # Adjust scale as needed

    # Add borders and stripes
    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor('black')
        cell.set_linewidth(0.5)
        if i == 0:  # Header row
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#D3D3D3')  # Light gray background
        elif i % 2 == 0:  # Even rows
            cell.set_facecolor('#F5F5F5')  # Very light gray
        else:  # Odd rows
            cell.set_facecolor('white')

    ax.set_title(title, fontsize=14)
    plt.show()
