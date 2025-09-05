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
