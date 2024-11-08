# components/utilities/due_date.py

from datetime import datetime, timedelta

def calculate_due_date(days_from_now=30):
    """
    Calculate a due date.
    
    Args:
        days_from_now (int): The number of days from today for the due date.
    
    Returns:
        str: Due date as an ISO 8601 formatted string.
    """
    due_date = datetime.now() + timedelta(days=days_from_now)
    return due_date.isoformat()  # Return as ISO format for consistency
