import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import calendar

# Import individual functions to have better control over plotting
from get_required_hours_per_month import get_required_hours_per_month
from get_expected_monthly_power_cons import get_expected_monthly_power_cons
from calculate_max_hours import calculate_max_hours
from display_table import display_table
from calculate_percentage_difference import calculate_percentage_difference

# Set page configuration
st.set_page_config(
    page_title="MetaSTAAQ - Electrolyzer Simulation Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e7d32;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">⚡ MetaSTAAQ Electrolyzer Simulation Dashboard</p>', unsafe_allow_html=True)

# Sidebar for parameters
st.sidebar.markdown("### 🔧 Simulation Parameters")

# Load default data file
default_file_path = 'processed_donnees_prix_spot_fr_2021_2025_month_8.csv'
try:
    data_content = pd.read_csv(default_file_path)
except FileNotFoundError:
    st.error("❌ Default data file not found. Please ensure the data file is in the correct location.")
    st.stop()

# Year selection
st.sidebar.markdown("#### 📅 Year Selection")
available_years = sorted(data_content['Annee'].unique()) if 'Annee' in data_content.columns else [2024, 2025]
selected_years = st.sidebar.multiselect(
    "Select years for analysis",
    options=available_years,
    default=[2024, 2025] if all(year in available_years for year in [2024, 2025]) else available_years[:2]
)

# Filter data by selected years
if selected_years:
    data_content = data_content[data_content['Annee'].isin(selected_years)]

# Electrolyzer parameters
st.sidebar.markdown("#### ⚡ Electrolyzer Parameters")
electrolyser_power = st.sidebar.slider(
    "Electrolyzer Power (MW)",
    min_value=1.0,
    max_value=20.0,
    value=5.0,
    step=0.5,
    help="Power capacity of the electrolyzer in MW"
)

electrolyser_specific_consumption = st.sidebar.slider(
    "Specific Consumption (kWh/Nm³ H₂)",
    min_value=4.0,
    max_value=6.0,
    value=4.8,
    step=0.1,
    help="Energy consumption per cubic meter of hydrogen produced"
)

service_ratio = st.sidebar.slider(
    "Service Ratio",
    min_value=0.8,
    max_value=1.0,
    value=0.98,
    step=0.01,
    help="Electrolyzer availability ratio (0-1)"
)

# Price parameters
st.sidebar.markdown("#### 💰 Price Parameters")
target_price_mode = st.sidebar.radio(
    "Spot Price Selection Mode",
    options=["Single Price", "Multiple Prices"],
    help="Choose to analyze single or multiple target spot prices"
)

if target_price_mode == "Single Price":
    target_prices = [st.sidebar.slider(
        "Target Spot Price (€/MWh)",
        min_value=5,
        max_value=50,
        value=15,
        step=1
    )]
else:
    price_range = st.sidebar.slider(
        "Spot Price Range (€/MWh)",
        min_value=5,
        max_value=50,
        value=(10, 30),
        step=5
    )
    price_step = st.sidebar.slider(
        "Spot Price Step (€/MWh)",
        min_value=1,
        max_value=10,
        value=5,
        step=1
    )
    target_prices = list(range(price_range[0], price_range[1] + 1, price_step))

# PV and PPA Price Parameters
pv_price = st.sidebar.slider(
    "PV Price (€/MWh)",
    min_value=0,
    max_value=100,
    value=50,
    step=5,
    help="Price of photovoltaic energy"
)

ppa_price = st.sidebar.slider(
    "PPA Price (€/MWh)",
    min_value=50,
    max_value=200,
    value=80,
    step=5,
    help="Power Purchase Agreement price"
)

# Calculate derived parameters
h2_flowrate = round((electrolyser_power * 1000) / electrolyser_specific_consumption)
stoechio_H2_CH4 = 4
ch4_flowrate = round(h2_flowrate / stoechio_H2_CH4)
ch4_density = 0.7168  # kg/Nm³ CH₄
ch4_kg_per_day = ch4_flowrate * 24 * ch4_density

# Display calculated parameters
st.sidebar.markdown("#### 📊 Calculated Parameters")
st.sidebar.metric("H₂ Flow Rate", f"{h2_flowrate} Nm³/h")
st.sidebar.metric("CH₄ Flow Rate", f"{ch4_flowrate} Nm³/h")
st.sidebar.metric("CH₄ Production", f"{ch4_kg_per_day:.1f} kg/day")
st.sidebar.metric("PV Price", f"{pv_price} €/MWh")
st.sidebar.metric("PPA Price", f"{ppa_price} €/MWh")

# Main content area
if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
    if data_content.empty:
        st.error("❌ No data available. Please upload a valid CSV file.")
    else:
        # Create placeholder for results
        results_placeholder = st.empty()
        
        with st.spinner("Running simulation..."):
            try:
                # Run custom simulation with Streamlit-compatible plotting
                all_results = []
                
                for i, target_price in enumerate(target_prices):
                    st.write(f"**Analyzing target spot price: {target_price} €/MWh**")
                    
                    # Run simulation components
                    expected_monthly_hours = get_required_hours_per_month(service_ratio)
                    expected_monthly_power = get_expected_monthly_power_cons(electrolyser_power, expected_monthly_hours)
                    result = calculate_max_hours(data_content, target_price)
                    df_result = display_table(result)
                    
                    # Calculate differences
                    df_hour_diff = calculate_percentage_difference(df_result, expected_monthly_hours)
                    df_power_consumption = df_result * electrolyser_power
                    df_power_diff = calculate_percentage_difference(df_power_consumption, expected_monthly_power)
                    
                    # Display results table
                    st.write("**📊 Available Hours per Month:**")
                    st.dataframe(df_result, use_container_width=True)
                    
                    # Create and display charts using full width
                    st.write("**📈 Available Hours Chart:**")
                    
                    # Chart 1: Available Hours (Full Width)
                    fig1, ax1 = plt.subplots(figsize=(12, 6))
                    df_plot = df_result.T
                    monthly_avg = df_plot.mean(axis=1)
                    
                    df_plot.plot(kind='bar', ax=ax1, legend=True)
                    
                    # Plot mean values as prominent points with labels
                    ax1.plot(range(len(monthly_avg)), monthly_avg.values, 
                           color='red', linestyle='--', marker='o', markersize=8, 
                           linewidth=2, label='Monthly Average', markerfacecolor='red', 
                           markeredgecolor='white', markeredgewidth=2)
                    
                    # Add value labels on the mean points
                    for i, (month, value) in enumerate(monthly_avg.items()):
                        ax1.annotate(f'{value:.0f}h', 
                                   (i, value), 
                                   textcoords="offset points", 
                                   xytext=(0, 10), 
                                   ha='center', 
                                   fontsize=9, 
                                   fontweight='bold',
                                   color='red',
                                   bbox=dict(boxstyle='round,pad=0.3', 
                                           facecolor='white', 
                                           edgecolor='red', 
                                           alpha=0.8))
                    
                    ax1.set_xlabel('Month')
                    ax1.set_ylabel('Available Hours')
                    ax1.set_title(f'Available Hours - {target_price}€/MWh')
                    ax1.tick_params(axis='x', rotation=45)
                    ax1.legend(loc='upper left')
                    
                    # Add second y-axis for power consumption
                    ax2 = ax1.twinx()
                    max_power_consumption = electrolyser_power * 24
                    ax2.set_ylabel('Power Consumption (MWh/day)', color='blue')
                    ax2.set_ylim(0, max_power_consumption)
                    ax2.tick_params(axis='y', labelcolor='blue')
                    
                    plt.tight_layout()
                    st.pyplot(fig1)
                    
                    st.write("**🔋 Monthly Energy Coverage:**")
                    
                    # Chart 2: Energy Coverage (Full Width)
                    pv_energy_kwh = {
                        "January": 41329.5, "February": 62809.8, "March": 100499.8,
                        "April": 128700.4, "May": 132130.6, "June": 133177.3,
                        "July": 136106.0, "August": 127150.4, "September": 112236.2,
                        "October": 79940.3, "November": 48793.6, "December": 40402.6
                    }
                    pv_energy_mwh = {month: kwh / 1000 for month, kwh in pv_energy_kwh.items()}
                    
                    days_in_month = {
                        "January": 31, "February": 28, "March": 31, "April": 30,
                        "May": 31, "June": 30, "July": 31, "August": 31,
                        "September": 30, "October": 31, "November": 30, "December": 31
                    }
                    
                    monthly_available_power = df_power_consumption.mean().to_dict()
                    max_monthly_consumption = {
                        month: electrolyser_power * 24 * service_ratio * days_in_month[month]
                        for month in days_in_month
                    }
                    
                    df_plot_data = pd.DataFrame({
                        'Maximum Consumption (MWh)': pd.Series(max_monthly_consumption),
                        'PV': pd.Series(pv_energy_mwh),
                        'Spot': pd.Series(monthly_available_power)
                    })
                    
                    df_plot_data['PPA'] = (
                        df_plot_data['Maximum Consumption (MWh)'] - 
                        df_plot_data['PV'] - 
                        df_plot_data['Spot']
                    ).clip(lower=0)
                    
                    month_order = list(calendar.month_name)[1:]
                    df_plot_data = df_plot_data.reindex(month_order)
                    
                    fig2, ax3 = plt.subplots(figsize=(12, 6))
                    df_plot_data[['PV', 'Spot', 'PPA']].plot(
                        kind='bar', stacked=True, ax=ax3, color=['blue', 'green', 'red']
                    )
                    
                    # Add percentage labels inside bars with white text
                    for i, month in enumerate(df_plot_data.index):
                        pv_val = df_plot_data.loc[month, 'PV']
                        spot_val = df_plot_data.loc[month, 'Spot']
                        ppa_val = df_plot_data.loc[month, 'PPA']
                        
                        # Use the sum of plotted segments as total (this is what's actually displayed in the chart)
                        total_plotted = pv_val + spot_val + ppa_val
                        
                        if total_plotted > 0:
                            # Calculate percentages based on plotted total
                            pv_pct = (pv_val / total_plotted) * 100
                            spot_pct = (spot_val / total_plotted) * 100
                            ppa_pct = (ppa_val / total_plotted) * 100
                            
                            # Position for text (middle of each bar segment)
                            pv_mid = pv_val / 2
                            spot_mid = pv_val + (spot_val / 2)
                            ppa_mid = pv_val + spot_val + (ppa_val / 2)
                            
                            # Add percentage text if segment is large enough to be visible (reduced threshold)
                            if pv_pct > 3:  # Show if percentage > 3%
                                ax3.text(i, pv_mid, f'{pv_pct:.1f}%', 
                                        ha='center', va='center', color='white', fontweight='bold', fontsize=9)
                            
                            if spot_pct > 3:
                                ax3.text(i, spot_mid, f'{spot_pct:.1f}%', 
                                        ha='center', va='center', color='white', fontweight='bold', fontsize=9)
                            
                            if ppa_pct > 3:
                                ax3.text(i, ppa_mid, f'{ppa_pct:.1f}%', 
                                        ha='center', va='center', color='white', fontweight='bold', fontsize=9)
                    
                    ax3.set_title(f'Monthly Energy Coverage - {target_price}€/MWh')
                    ax3.set_xlabel('Month')
                    ax3.set_ylabel('Energy (MWh)')
                    ax3.tick_params(axis='x', rotation=45)
                    
                    plt.tight_layout()
                    st.pyplot(fig2)
                    
                    # Store results
                    all_results.append({
                        'target_price': target_price,
                        'df_result': df_result,
                        'df_power_consumption': df_power_consumption,
                        'monthly_avg_hours': df_result.mean().mean(),
                        'monthly_avg_power': df_power_consumption.mean().mean()
                    })
                    
                    st.success(f"✅ Completed analysis for {target_price} €/MWh")
                    
                    if i < len(target_prices) - 1:
                        st.markdown("---")
                
                st.success(f"🎉 Simulation completed for {len(target_prices)} price point(s)!")
                
                # Add comparison summary if multiple prices
                if len(all_results) > 1:
                    st.markdown("---")
                    st.markdown("### 📈 Price Comparison Summary")
                    
                    comparison_data = []
                    for result in all_results:
                        comparison_data.append({
                            'Target Spot Price (€/MWh)': result['target_price'],
                            'Avg Monthly Hours': f"{result['monthly_avg_hours']:.1f}",
                            'Avg Monthly Power (MWh)': f"{result['monthly_avg_power']:.1f}"
                        })
                    
                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(comparison_df, use_container_width=True)
                    
                    # Price comparison chart
                    fig_comp, (ax_comp1, ax_comp2) = plt.subplots(1, 2, figsize=(12, 5))
                    
                    prices = [r['target_price'] for r in all_results]
                    hours = [r['monthly_avg_hours'] for r in all_results]
                    power = [r['monthly_avg_power'] for r in all_results]
                    
                    ax_comp1.plot(prices, hours, 'o-', color='blue', linewidth=2, markersize=8)
                    ax_comp1.set_xlabel('Target Spot Price (€/MWh)')
                    ax_comp1.set_ylabel('Average Monthly Hours')
                    ax_comp1.set_title('Hours vs Price')
                    ax_comp1.grid(True, alpha=0.3)
                    
                    ax_comp2.plot(prices, power, 'o-', color='green', linewidth=2, markersize=8)
                    ax_comp2.set_xlabel('Target Spot Price (€/MWh)')
                    ax_comp2.set_ylabel('Average Monthly Power (MWh)')
                    ax_comp2.set_title('Power vs Price')
                    ax_comp2.grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    st.pyplot(fig_comp)
                
            except Exception as e:
                st.error(f"❌ Error running simulation: {str(e)}")
                st.exception(e)  # Show full error details for debugging

# Compact Summary Section
st.markdown("---")
st.markdown("### 📋 Quick Summary")

col_sum1, col_sum2, col_sum3 = st.columns(3)
with col_sum1:
    st.metric("Selected Years", f"{len(selected_years)} years")
with col_sum2:
    st.metric("Electrolyzer Power", f"{electrolyser_power} MW")
with col_sum3:
    st.metric("Target Spot Prices", f"{len(target_prices)} price(s)")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>MetaSTAAQ Electrolyzer Simulation Dashboard | 
        Built with Streamlit | 
        Data-driven energy analysis</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Instructions
with st.expander("ℹ️ How to use this dashboard"):
    st.markdown("""
    1. **Select Years**: Choose which years to include in the analysis
    2. **Set Parameters**: Adjust electrolyzer power, consumption, and service ratio
    3. **Choose Prices**: Select single or multiple target spot prices for analysis
    4. **Run Simulation**: Click the "Run Simulation" button to start the analysis
    5. **View Results**: Charts and tables will be displayed below
    
    **Data Source**: The dashboard uses pre-loaded spot price data for France (2021-2025).
    """)
