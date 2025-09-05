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
