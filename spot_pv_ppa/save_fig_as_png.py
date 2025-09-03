# -*- coding: utf-8 -*-
"""
Function to save matplotlib figures as PNG files.
"""

import matplotlib.pyplot as plt


def save_fig_as_png(fig, filename):
    """
    Saves a matplotlib figure as a PNG file.

    Parameters:
        fig (matplotlib.figure.Figure): The figure to save.
        filename (str): The name of the file to save the figure to (including .png extension).
    """
    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)  # Close the figure after saving to free up memory
