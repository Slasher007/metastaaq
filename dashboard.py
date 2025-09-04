import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import calendar
from mpl_toolkits.mplot3d import Axes3D

# Import individual functions to have better control over plotting
from calculate_max_hours import calculate_max_hours
from display_table import display_table
from calculate_percentage_difference import calculate_percentage_difference

# Set page configuration
st.set_page_config(
    page_title="MetaSTAAQ - LCOE Simulation Dashboard",
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

st.markdown('<p class="main-header">⚡ MetaSTAAQ LCOE Simulation Dashboard</p>', unsafe_allow_html=True)

# Sidebar with logo and parameters
try:
    st.sidebar.image("STAAQ_HD.jpg", width=180)
except FileNotFoundError:
    st.sidebar.warning("⚠️ Logo file 'STAAQ_HD.jpg' not found")

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

# Monthly Service Ratios
st.sidebar.markdown("#### 📅 Monthly Service Ratios")
st.sidebar.markdown("*Set individual availability ratios for each month (0.0 = off, 1.0 = always on)*")

# Create two columns for better layout
col1, col2 = st.sidebar.columns(2)

# Create monthly service ratio sliders
monthly_service_ratios = {}
months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]

# First 6 months in left column
with col1:
    for month in months[:6]:
        monthly_service_ratios[month] = st.slider(
            f"{month[:3]}",  # Short month name
            min_value=0.0,
    max_value=1.0,
    value=0.98,
    step=0.01,
            key=f"service_{month}",
            help=f"Service ratio for {month}"
        )

# Last 6 months in right column  
with col2:
    for month in months[6:]:
        monthly_service_ratios[month] = st.slider(
            f"{month[:3]}",  # Short month name
            min_value=0.0,
            max_value=1.0,
            value=0.98,
            step=0.01,
            key=f"service_{month}",
            help=f"Service ratio for {month}"
        )

# Add quick preset buttons for common scenarios
st.sidebar.markdown("**Quick Presets:**")
preset_col1, preset_col2, preset_col3 = st.sidebar.columns(3)

with preset_col1:
    if st.button("All Max", help="Set all months to 1.0"):
        for month in months:
            st.session_state[f"service_{month}"] = 1.0
        st.rerun()

with preset_col2:
    if st.button("All 98%", help="Set all months to 0.98"):
        for month in months:
            st.session_state[f"service_{month}"] = 0.98
        st.rerun()

with preset_col3:
    if st.button("All Off", help="Set all months to 0.0"):
        for month in months:
            st.session_state[f"service_{month}"] = 0.0
        st.rerun()

# Calculate average service ratio for display purposes
avg_service_ratio = sum(monthly_service_ratios.values()) / len(monthly_service_ratios)

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

# Create function to calculate monthly required hours with individual service ratios
def get_required_hours_per_month_custom(monthly_service_ratios: dict) -> dict:
    """
    Calculate required hours per month using individual monthly service ratios.
    
    Parameters:
        monthly_service_ratios (dict): Service ratio for each month
        
    Returns:
        dict: Required hours for each month
    """
    days_per_month = {
        "January": 31, "February": 28, "March": 31, "April": 30,
        "May": 31, "June": 30, "July": 31, "August": 31,
        "September": 30, "October": 31, "November": 30, "December": 31
    }
    
    return {
        month: round(days_per_month[month] * 24 * monthly_service_ratios[month], 0)
        for month in days_per_month.keys()
    }

# Create function to calculate monthly expected power consumption
def get_expected_monthly_power_cons_custom(electrolyser_power: float, monthly_required_hours: dict) -> dict:
    """
    Calculate expected monthly power consumption using monthly required hours.
    
    Parameters:
        electrolyser_power (float): Electrolyzer power in MW
        monthly_required_hours (dict): Required hours for each month
        
    Returns:
        dict: Expected power consumption for each month in MWh
    """
    return {
        month: electrolyser_power * hours
        for month, hours in monthly_required_hours.items()
    }

# Calculate derived parameters
h2_flowrate = round((electrolyser_power * 1000) / electrolyser_specific_consumption)
stoechio_H2_CH4 = 4
ch4_flowrate = round(h2_flowrate / stoechio_H2_CH4)
ch4_density = 0.7168  # kg/Nm³ CH₄
ch4_kg_per_day = ch4_flowrate * 24 * ch4_density

# Calculate monthly CH4 production based on service ratios
monthly_ch4_production = {
    month: ch4_flowrate * 24 * ratio * (31 if month in ["January", "March", "May", "July", "August", "October", "December"] 
                                       else 30 if month != "February" else 28) * ch4_density
    for month, ratio in monthly_service_ratios.items()
}

# Calculate LCOE (Levelized Cost of Energy)
# This will be calculated dynamically based on the energy mix and prices
def calculate_lcoe(pv_energy_mwh, spot_energy_dict, ppa_energy_dict, pv_price, spot_price, ppa_price):
    """Calculate the Levelized Cost of Energy based on energy mix and prices"""
    total_cost = 0
    total_energy = 0
    
    for month in pv_energy_mwh.keys():
        # Get energy amounts for each source
        pv_energy = pv_energy_mwh[month]
        spot_energy = spot_energy_dict.get(month, 0)
        ppa_energy = ppa_energy_dict.get(month, 0)
        
        # Calculate costs
        pv_cost = pv_energy * pv_price
        spot_cost = spot_energy * spot_price
        ppa_cost = ppa_energy * ppa_price
        
        # Add to totals
        total_cost += pv_cost + spot_cost + ppa_cost
        total_energy += pv_energy + spot_energy + ppa_energy
    
    return total_cost / total_energy if total_energy > 0 else 0

# Display calculated parameters
st.sidebar.markdown("#### 📊 Calculated Parameters")
st.sidebar.metric("H₂ Flow Rate", f"{h2_flowrate} Nm³/h")
st.sidebar.metric("CH₄ Flow Rate", f"{ch4_flowrate} Nm³/h")
st.sidebar.metric("Avg Service Ratio", f"{avg_service_ratio:.1%}")

# Show monthly CH4 production summary
total_yearly_ch4_kg = sum(monthly_ch4_production.values())
total_yearly_ch4_tonnes = total_yearly_ch4_kg / 1000
st.sidebar.metric("Yearly CH₄ Production", f"{total_yearly_ch4_tonnes:,.0f} Tonnes")

# Add expandable section for monthly details
with st.sidebar.expander("📅 Monthly Details"):
    for month, production in monthly_ch4_production.items():
        monthly_production_tonnes = production / 1000
        service_pct = monthly_service_ratios[month] * 100
        st.write(f"**{month[:3]}**: {monthly_production_tonnes:.1f} Tonnes ({service_pct:.0f}%)")

# Add parameter change detection using session state
if 'last_params' not in st.session_state:
    st.session_state.last_params = {}

# Current parameters
current_params = {
    'years': tuple(sorted(selected_years)) if selected_years else (),
    'power': electrolyser_power,
    'consumption': electrolyser_specific_consumption,
    'monthly_service_ratios': tuple(sorted(monthly_service_ratios.items())),
    'target_prices': tuple(target_prices),
    'pv_price': pv_price,
    'ppa_price': ppa_price
}

# Check if parameters have changed
params_changed = st.session_state.last_params != current_params

# Update session state
st.session_state.last_params = current_params.copy()

# Add manual refresh button (optional)
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### 📊 Simulation Results")
    if params_changed:
        st.info("🔄 Parameters changed - Results updating automatically...")

with col2:
    manual_refresh = st.button("🔄 Manual Refresh", help="Force refresh the simulation")

# Add a visual summary of monthly service ratios before results
st.markdown("#### 📅 Current Monthly Service Ratios")
service_ratio_df = pd.DataFrame({
    'Month': list(monthly_service_ratios.keys()),
    'Service Ratio': [f"{ratio:.1%}" for ratio in monthly_service_ratios.values()],
    'Service Ratio (Decimal)': list(monthly_service_ratios.values())
})

# Create a bar chart for service ratios
fig_service, ax_service = plt.subplots(figsize=(12, 4))
bars = ax_service.bar(range(len(monthly_service_ratios)), 
                     list(monthly_service_ratios.values()),
                     color=['lightgreen' if ratio >= 0.9 else 'orange' if ratio >= 0.5 else 'lightcoral' 
                           for ratio in monthly_service_ratios.values()])

# Add value labels on bars
for i, (month, ratio) in enumerate(monthly_service_ratios.items()):
    ax_service.text(i, ratio + 0.01, f'{ratio:.0%}', 
                   ha='center', va='bottom', fontweight='bold', fontsize=10)

ax_service.set_xticks(range(len(monthly_service_ratios)))
ax_service.set_xticklabels([month[:3] for month in monthly_service_ratios.keys()], rotation=45)
ax_service.set_ylabel('Service Ratio')
ax_service.set_title('Monthly Service Ratios (Green: ≥90%, Orange: 50-90%, Red: <50%)')
ax_service.set_ylim(0, 1.1)
ax_service.grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig_service)

# Auto-run simulation when parameters change or manual refresh is clicked
run_simulation = params_changed or manual_refresh or 'simulation_run' not in st.session_state

if run_simulation:
    if data_content.empty:
        st.error("❌ No data available. Please upload a valid CSV file.")
    else:
        # Create placeholder for results
        results_placeholder = st.empty()
        
        # Show appropriate loading message
        loading_message = "🔄 Updating simulation with new parameters..." if params_changed else "🚀 Running simulation..."
        
        with st.spinner(loading_message):
            try:
                # Run custom simulation with Streamlit-compatible plotting
                all_results = []
                
                for i, target_price in enumerate(target_prices):
                    st.write(f"**Analyzing target spot price: {target_price} €/MWh**")
                    
                    # Run simulation components using monthly service ratios
                    expected_monthly_hours = get_required_hours_per_month_custom(monthly_service_ratios)
                    expected_monthly_power = get_expected_monthly_power_cons_custom(electrolyser_power, expected_monthly_hours)
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
                    ax1.set_title(f'Spot Available Hours - {target_price}€/MWh\n(Service ratios: {", ".join([f"{month[:3]}:{monthly_service_ratios[month]:.0%}" for month in monthly_service_ratios])})')
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
                    
                    # PV Production Chart Section
                    st.write("**☀️ Monthly PV Production (Meaux Location):**")
                    try:
                        # Create 2x2 grid layout for the images
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.image("meaux_maps_location.png", caption="Meaux Location Map", use_container_width=True)
                            st.image("meaux_simulation_output.png", caption="Simulation Output", use_container_width=True)
                        
                        with col2:
                            st.image("meaux_pv_config.png", caption="PV Configuration", use_container_width=True)
                            st.image("monthly_pv_meaux.png", caption="Monthly PV Energy Production", use_container_width=True)
                        
                        st.info("📍 **PV Installation with tracking system**: Analysis based on 1 hectare solar panel surface area in Meaux. Data source: PVGIS (Photovoltaic Geographical Information System)")
                    except FileNotFoundError as e:
                        st.warning(f"⚠️ One or more PV images not found: {str(e)}")
                    
                    st.write("**🔋 Monthly Energy Coverage:**")
                    
                    # Chart 2: Energy Coverage (Full Width)
                    pv_energy_kwh = {
                        "January": 53458.33, "February": 80213.5, "March": 130815.4,
                        "April": 173641.0, "May": 180419.5, "June":187157.5 ,
                        "July": 191786.5, "August": 171279.3, "September": 148726.1,
                        "October": 102391.7, "November": 62860.4, "December": 55020.23
                    }
                    pv_energy_mwh = {month: kwh / 1000 for month, kwh in pv_energy_kwh.items()}
                    
                    days_in_month = {
                        "January": 31, "February": 28, "March": 31, "April": 30,
                        "May": 31, "June": 30, "July": 31, "August": 31,
                        "September": 30, "October": 31, "November": 30, "December": 31
                    }
                    
                    monthly_available_power = df_power_consumption.mean().to_dict()
                    max_monthly_consumption = {
                        month: electrolyser_power * 24 * monthly_service_ratios[month] * days_in_month[month]
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
                    
                    # Calculate LCOE for this target price
                    pv_energy_dict = df_plot_data['PV'].to_dict()
                    spot_energy_dict = df_plot_data['Spot'].to_dict()
                    ppa_energy_dict = df_plot_data['PPA'].to_dict()
                    
                    lcoe = calculate_lcoe(pv_energy_dict, spot_energy_dict, ppa_energy_dict, 
                                        pv_price, target_price, ppa_price)
                    
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
                    
                    ax3.set_title(f'Monthly Energy Coverage')
                    ax3.set_xlabel('Month')
                    ax3.set_ylabel('Energy (MWh)')
                    ax3.tick_params(axis='x', rotation=45)
                    
                    plt.tight_layout()
                    st.pyplot(fig2)
                    
                    # Create pie chart for energy coverage distribution
                    st.write("**🥧 Energy Coverage Distribution:**")
                    
                    # Calculate total energy for each source
                    total_pv_energy = sum(df_plot_data['PV'])
                    total_spot_energy = sum(df_plot_data['Spot'])
                    total_ppa_energy = sum(df_plot_data['PPA'])
                    
                    # Create pie chart data
                    pie_data = [total_pv_energy, total_spot_energy, total_ppa_energy]
                    pie_labels = ['PV', 'Spot', 'PPA']
                    pie_colors = ['blue', 'green', 'red']
                    
                    # Filter out zero values for cleaner pie chart
                    filtered_data = []
                    filtered_labels = []
                    filtered_colors = []
                    
                    for i, value in enumerate(pie_data):
                        if value > 0:
                            filtered_data.append(value)
                            filtered_labels.append(pie_labels[i])
                            filtered_colors.append(pie_colors[i])
                    
                    if filtered_data:  # Only create pie chart if there's data
                        fig3, ax4 = plt.subplots(figsize=(4, 3))
                        
                        # Create pie chart with percentages
                        wedges, texts, autotexts = ax4.pie(
                            filtered_data, 
                            labels=filtered_labels, 
                            colors=filtered_colors,
                            autopct='%1.1f%%',
                            startangle=90,
                            textprops={'fontsize': 12, 'fontweight': 'bold'}
                        )
                        
                        # Enhance the appearance
                        for autotext in autotexts:
                            autotext.set_color('white')
                            autotext.set_fontweight('bold')
                        
                        ax4.set_title(f'Energy Coverage Distribution', 
                                     fontsize=14, fontweight='bold', pad=20)
                        
                        # Add legend with energy values
                        legend_labels = [f'{label}: {value:.1f} MWh' for label, value in zip(filtered_labels, filtered_data)]
                        ax4.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
                        
                        plt.tight_layout()
                        st.pyplot(fig3)
                    
                    # Display LCOE
                    st.metric(f"**LCOE (Levelized Cost of Energy) for {target_price}€/MWh spot price:**", 
                             f"{lcoe:.2f} €/MWh")
                    
                    # Create detailed monthly breakdown table
                    st.write("**📊 Monthly Energy Breakdown:**")
                    
                    monthly_breakdown = []
                    for month in df_plot_data.index:
                        pv_energy = df_plot_data.loc[month, 'PV']
                        spot_energy = df_plot_data.loc[month, 'Spot']
                        ppa_energy = df_plot_data.loc[month, 'PPA']
                        total_energy = pv_energy + spot_energy + ppa_energy
                        
                        # Calculate coverage ratios
                        pv_ratio = (pv_energy / total_energy * 100) if total_energy > 0 else 0
                        spot_ratio = (spot_energy / total_energy * 100) if total_energy > 0 else 0
                        ppa_ratio = (ppa_energy / total_energy * 100) if total_energy > 0 else 0
                        
                        # Calculate costs
                        pv_cost = pv_energy * pv_price
                        spot_cost = spot_energy * target_price
                        ppa_cost = ppa_energy * ppa_price
                        total_cost = pv_cost + spot_cost + ppa_cost
                        
                        monthly_breakdown.append({
                            'Month': month,
                            'PV Energy (MWh)': f"{pv_energy:.1f}",
                            'PV Coverage (%)': f"{pv_ratio:.1f}%",
                            'PV Cost (€)': f"{pv_cost:,.0f}",
                            'Spot Energy (MWh)': f"{spot_energy:.1f}",
                            'Spot Coverage (%)': f"{spot_ratio:.1f}%",
                            'Spot Cost (€)': f"{spot_cost:,.0f}",
                            'PPA Energy (MWh)': f"{ppa_energy:.1f}",
                            'PPA Coverage (%)': f"{ppa_ratio:.1f}%",
                            'PPA Cost (€)': f"{ppa_cost:,.0f}",
                            'Total Energy (MWh)': f"{total_energy:.1f}",
                            'Total Cost (€)': f"{total_cost:,.0f}",
                            'Avg Cost (€/MWh)': f"{total_cost/total_energy:.2f}" if total_energy > 0 else "0.00"
                        })
                    
                    breakdown_df = pd.DataFrame(monthly_breakdown)
                    
                    # Calculate yearly totals and averages
                    total_pv_energy = sum(df_plot_data['PV'])
                    total_spot_energy = sum(df_plot_data['Spot'])
                    total_ppa_energy = sum(df_plot_data['PPA'])
                    total_energy_year = total_pv_energy + total_spot_energy + total_ppa_energy
                    
                    total_pv_cost = total_pv_energy * pv_price
                    total_spot_cost = total_spot_energy * target_price
                    total_ppa_cost = total_ppa_energy * ppa_price
                    total_cost_year = total_pv_cost + total_spot_cost + total_ppa_cost
                    
                    # Calculate yearly averages for percentages
                    avg_pv_ratio = (total_pv_energy / total_energy_year * 100) if total_energy_year > 0 else 0
                    avg_spot_ratio = (total_spot_energy / total_energy_year * 100) if total_energy_year > 0 else 0
                    avg_ppa_ratio = (total_ppa_energy / total_energy_year * 100) if total_energy_year > 0 else 0
                    
                    # Add yearly average row
                    yearly_average = {
                        'Month': '📊 YEARLY TOTAL',
                        'PV Energy (MWh)': f"{total_pv_energy:.1f}",
                        'PV Coverage (%)': f"{avg_pv_ratio:.1f}%",
                        'PV Cost (€)': f"{total_pv_cost:,.0f}",
                        'Spot Energy (MWh)': f"{total_spot_energy:.1f}",
                        'Spot Coverage (%)': f"{avg_spot_ratio:.1f}%",
                        'Spot Cost (€)': f"{total_spot_cost:,.0f}",
                        'PPA Energy (MWh)': f"{total_ppa_energy:.1f}",
                        'PPA Coverage (%)': f"{avg_ppa_ratio:.1f}%",
                        'PPA Cost (€)': f"{total_ppa_cost:,.0f}",
                        'Total Energy (MWh)': f"{total_energy_year:.1f}",
                        'Total Cost (€)': f"{total_cost_year:,.0f}",
                        'Avg Cost (€/MWh)': f"{total_cost_year/total_energy_year:.2f}" if total_energy_year > 0 else "0.00"
                    }
                    
                    # Add the yearly row to the dataframe
                    breakdown_df = pd.concat([breakdown_df, pd.DataFrame([yearly_average])], ignore_index=True)
                    
                    # Style the dataframe to highlight the yearly total row
                    def highlight_yearly_row(row):
                        if row.name == len(breakdown_df) - 1:  # Last row (yearly total)
                            return ['background-color: #1f77b4; color: white; font-weight: bold'] * len(row)
                        return [''] * len(row)
                    
                    styled_df = breakdown_df.style.apply(highlight_yearly_row, axis=1)
                    
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Store results
                    all_results.append({
                        'target_price': target_price,
                        'df_result': df_result,
                        'df_power_consumption': df_power_consumption,
                        'monthly_avg_hours': df_result.mean().mean(),
                        'monthly_avg_power': df_power_consumption.mean().mean(),
                        'lcoe': lcoe
                    })
                    

                    
                    if i < len(target_prices) - 1:
                        st.markdown("---")
                

                

                
                # Add comparison summary if multiple prices
                if len(all_results) > 1:
                    st.markdown("---")
                    st.markdown("### 📈 Price Comparison Summary")
                    
                    comparison_data = []
                    for result in all_results:
                        comparison_data.append({
                            'Target Spot Price (€/MWh)': result['target_price'],
                            'Avg Monthly Hours': f"{result['monthly_avg_hours']:.1f}",
                            'Avg Monthly Power (MWh)': f"{result['monthly_avg_power']:.1f}",
                            'LCOE (€/MWh)': f"{result['lcoe']:.2f}"
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
                
                # Add comprehensive 3D analysis
                st.markdown("---")
                st.write("**🎯 Complete 3D Analysis: All Three Price Sources:**")

                base_pv_energy = sum(df_plot_data['PV'])
                base_spot_energy = sum(df_plot_data['Spot'])
                base_ppa_energy = sum(df_plot_data['PPA'])
                total_energy = base_pv_energy + base_spot_energy + base_ppa_energy

                if total_energy > 0:
                    # Create a comprehensive figure with multiple visualization approaches
                    fig_complete = plt.figure(figsize=(16, 12))
                    
                    # Method 1: 3D Scatter plot with color coding
                    ax1 = fig_complete.add_subplot(221, projection='3d')
                    
                    # Create sample points across all three dimensions
                    n_samples = 100
                    pv_samples = np.random.uniform(0, 100, n_samples)
                    ppa_samples = np.random.uniform(50, 150, n_samples)
                    spot_samples = np.random.uniform(5, 50, n_samples)
                    
                    # Calculate LCOE for each sample point
                    lcoe_samples = []
                    for i in range(n_samples):
                        pv_cost = base_pv_energy * pv_samples[i]
                        spot_cost = base_spot_energy * spot_samples[i]
                        ppa_cost = base_ppa_energy * ppa_samples[i]
                        lcoe = (pv_cost + spot_cost + ppa_cost) / total_energy
                        lcoe_samples.append(lcoe)
                    
                    # Create 3D scatter plot with color-coded LCOE
                    scatter = ax1.scatter(pv_samples, ppa_samples, spot_samples, 
                                        c=lcoe_samples, cmap='viridis', s=50, alpha=0.7)
                    
                    # Add current point
                    current_lcoe_3d = (base_pv_energy * pv_price + base_spot_energy * target_prices[0] + base_ppa_energy * ppa_price) / total_energy
                    ax1.scatter([pv_price], [ppa_price], [target_prices[0]], 
                              color='red', s=200, marker='*', label=f'Current: {current_lcoe_3d:.2f}€/MWh')
                    
                    ax1.set_xlabel('PV Price (€/MWh)')
                    ax1.set_ylabel('PPA Price (€/MWh)')
                    ax1.set_zlabel('Spot Price (€/MWh)')
                    ax1.set_title('3D Price Space\n(Color = LCOE)', fontweight='bold')
                    ax1.legend()
                    
                    # Add colorbar for scatter plot
                    cbar1 = plt.colorbar(scatter, ax=ax1, shrink=0.8, aspect=20)
                    cbar1.set_label('LCOE (€/MWh)')
                    
                    # Method 2: Multiple 2D contour plots
                    ax2 = fig_complete.add_subplot(222)
                    
                    # Create contour plot for PV vs PPA (at current spot price)
                    pv_contour = np.linspace(0, 100, 20)
                    ppa_contour = np.linspace(50, 150, 20)
                    PV_cont, PPA_cont = np.meshgrid(pv_contour, ppa_contour)
                    
                    LCOE_contour = np.zeros_like(PV_cont)
                    for i in range(len(ppa_contour)):
                        for j in range(len(pv_contour)):
                            pv_cost = base_pv_energy * PV_cont[i, j]
                            spot_cost = base_spot_energy * target_prices[0]  # Fixed spot
                            ppa_cost = base_ppa_energy * PPA_cont[i, j]
                            LCOE_contour[i, j] = (pv_cost + spot_cost + ppa_cost) / total_energy
                    
                    contour = ax2.contourf(PV_cont, PPA_cont, LCOE_contour, levels=15, cmap='viridis', alpha=0.8)
                    contour_lines = ax2.contour(PV_cont, PPA_cont, LCOE_contour, levels=15, colors='black', alpha=0.4, linewidths=0.5)
                    ax2.clabel(contour_lines, inline=True, fontsize=8, fmt='%.1f')
                    
                    # Add current point
                    ax2.plot(pv_price, ppa_price, 'r*', markersize=15, label=f'Current: {current_lcoe_3d:.2f}€/MWh')
                    
                    ax2.set_xlabel('PV Price (€/MWh)')
                    ax2.set_ylabel('PPA Price (€/MWh)')
                    ax2.set_title(f'LCOE Contours: PV vs PPA\n(Spot = {target_prices[0]}€/MWh)', fontweight='bold')
                    ax2.legend()
                    
                    plt.colorbar(contour, ax=ax2, label='LCOE (€/MWh)')
                    
                    # Method 3: Parallel coordinates plot
                    ax3 = fig_complete.add_subplot(223)
                    
                    # Create multiple scenarios
                    n_scenarios = 50
                    scenarios_pv = np.linspace(0, 100, n_scenarios)
                    scenarios_ppa = np.linspace(50, 150, n_scenarios)
                    scenarios_spot = np.linspace(5, 50, n_scenarios)
                    
                    # Calculate LCOE for different scenarios
                    for i in range(0, n_scenarios, 5):  # Every 5th scenario to avoid clutter
                        pv_p = scenarios_pv[i]
                        ppa_p = scenarios_ppa[i]
                        spot_p = scenarios_spot[i]
                        
                        lcoe_scenario = (base_pv_energy * pv_p + base_spot_energy * spot_p + base_ppa_energy * ppa_p) / total_energy
                        
                        # Normalize values for parallel coordinates
                        pv_norm = pv_p / 100
                        ppa_norm = (ppa_p - 50) / 100
                        spot_norm = (spot_p - 5) / 45
                        lcoe_norm = (lcoe_scenario - min(lcoe_samples)) / (max(lcoe_samples) - min(lcoe_samples))
                        
                        # Plot line connecting all dimensions
                        ax3.plot([0, 1, 2, 3], [pv_norm, ppa_norm, spot_norm, lcoe_norm], 
                                alpha=0.3, color=plt.cm.viridis(lcoe_norm))
                    
                    # Current scenario
                    current_pv_norm = pv_price / 100
                    current_ppa_norm = (ppa_price - 50) / 100
                    current_spot_norm = (target_prices[0] - 5) / 45
                    current_lcoe_norm = (current_lcoe_3d - min(lcoe_samples)) / (max(lcoe_samples) - min(lcoe_samples))
                    
                    ax3.plot([0, 1, 2, 3], [current_pv_norm, current_ppa_norm, current_spot_norm, current_lcoe_norm], 
                            'r-', linewidth=3, marker='o', markersize=8, label='Current Configuration')
                    
                    ax3.set_xticks([0, 1, 2, 3])
                    ax3.set_xticklabels(['PV\n(0-100€)', 'PPA\n(50-150€)', 'Spot\n(5-50€)', 'LCOE\n(normalized)'])
                    ax3.set_ylabel('Normalized Values (0-1)')
                    ax3.set_title('Parallel Coordinates:\nPrice Dependencies', fontweight='bold')
                    ax3.legend()
                    ax3.grid(True, alpha=0.3)
                    
                    # Method 4: Heatmap matrix showing price combinations
                    ax4 = fig_complete.add_subplot(224)
                    
                    # Create a simplified grid for heatmap
                    pv_heat = np.linspace(0, 100, 10)
                    ppa_heat = np.linspace(50, 150, 10)
                    
                    # Use current spot price
                    spot_fixed = target_prices[0]
                    
                    heat_matrix = np.zeros((len(ppa_heat), len(pv_heat)))
                    for i, ppa_p in enumerate(ppa_heat):
                        for j, pv_p in enumerate(pv_heat):
                            pv_cost = base_pv_energy * pv_p
                            spot_cost = base_spot_energy * spot_fixed
                            ppa_cost = base_ppa_energy * ppa_p
                            heat_matrix[i, j] = (pv_cost + spot_cost + ppa_cost) / total_energy
                    
                    heatmap = ax4.imshow(heat_matrix, cmap='viridis', aspect='auto', origin='lower')
                    
                    # Add text annotations
                    for i in range(len(ppa_heat)):
                        for j in range(len(pv_heat)):
                            text = ax4.text(j, i, f'{heat_matrix[i, j]:.1f}',
                                          ha="center", va="center", color="white", fontsize=8)
                    
                    # Find current position in grid
                    current_j = np.argmin(np.abs(pv_heat - pv_price))
                    current_i = np.argmin(np.abs(ppa_heat - ppa_price))
                    ax4.plot(current_j, current_i, 'r*', markersize=20)
                    
                    ax4.set_xticks(range(len(pv_heat)))
                    ax4.set_xticklabels([f'{x:.0f}' for x in pv_heat])
                    ax4.set_yticks(range(len(ppa_heat)))
                    ax4.set_yticklabels([f'{y:.0f}' for y in ppa_heat])
                    ax4.set_xlabel('PV Price (€/MWh)')
                    ax4.set_ylabel('PPA Price (€/MWh)')
                    ax4.set_title(f'LCOE Heatmap\n(Spot = {spot_fixed}€/MWh)', fontweight='bold')
                    
                    plt.colorbar(heatmap, ax=ax4, label='LCOE (€/MWh)')
                    
                    plt.suptitle('Comprehensive LCOE Analysis: All Three Price Sources', 
                                fontsize=16, fontweight='bold', y=0.98)
                    plt.tight_layout()
                    st.pyplot(fig_complete)
                    
                    # Add comprehensive insights
                    st.write("**🔍 Multi-Dimensional Analysis Insights:**")
                    
                    # Calculate optimal combinations
                    min_lcoe_overall = min(lcoe_samples)
                    max_lcoe_overall = max(lcoe_samples)
                    min_idx = lcoe_samples.index(min_lcoe_overall)
                    
                    optimal_combination = {
                        'Analysis Type': ['3D Scatter Plot', 'Current Configuration', 'Optimal Found', 'Range Analysis'],
                        'PV Price (€/MWh)': [f'{np.mean(pv_samples):.1f} (avg)', f'{pv_price:.1f}', 
                                           f'{pv_samples[min_idx]:.1f}', f'{min(pv_samples):.1f}-{max(pv_samples):.1f}'],
                        'PPA Price (€/MWh)': [f'{np.mean(ppa_samples):.1f} (avg)', f'{ppa_price:.1f}', 
                                            f'{ppa_samples[min_idx]:.1f}', f'{min(ppa_samples):.1f}-{max(ppa_samples):.1f}'],
                        'Spot Price (€/MWh)': [f'{np.mean(spot_samples):.1f} (avg)', f'{target_prices[0]:.1f}', 
                                             f'{spot_samples[min_idx]:.1f}', f'{min(spot_samples):.1f}-{max(spot_samples):.1f}'],
                        'LCOE (€/MWh)': [f'{np.mean(lcoe_samples):.2f} (avg)', f'{current_lcoe_3d:.2f}', 
                                       f'{min_lcoe_overall:.2f}', f'{min_lcoe_overall:.2f}-{max_lcoe_overall:.2f}']
                    }
                    
                    comprehensive_df = pd.DataFrame(optimal_combination)
                    st.dataframe(comprehensive_df, use_container_width=True)
                else:
                    st.warning("⚠️ No energy data available for 3D analysis. Please check the simulation parameters.")
                
                # Mark simulation as completed
                st.session_state.simulation_run = True
                
            except Exception as e:
                st.error(f"❌ Error running simulation: {str(e)}")
                st.exception(e)  # Show full error details for debugging
else:
    # Show message when no simulation needs to be run
    if 'simulation_run' in st.session_state:
        st.success("✅ Simulation up to date. Change any parameter above to refresh results.")
    else:
        st.info("👆 Adjust parameters in the sidebar to start the simulation.")



# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #666;'>
        <p>MetaSTAAQ LCOE Simulation Dashboard | 
        Built with Streamlit | 
        Data-driven energy analysis</p>
        <p style='margin-top: 10px; font-size: 14px;'>
        © STAAQ Technology All Rights Reserved {pd.Timestamp.now().year}
        </p>
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
    4. **Auto-Update**: Results update automatically when you change any parameter!
    5. **Manual Refresh**: Use the "Manual Refresh" button if needed
    6. **View Results**: Charts and tables are displayed below the parameters
    
    
    **Data Source**: The dashboard uses pre-loaded spot price data for France (2021-2025).
    """)
