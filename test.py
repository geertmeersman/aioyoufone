from datetime import datetime, timedelta


# Function to calculate start date, end date, and percentage elapsed in the billing period
def percentage_elapsed(remaining_days):
    # Get the current datetime
    current_datetime = datetime.now()

    # Calculate the end datetime (today + remaining days) at midnight
    end_datetime = datetime(
        current_datetime.year, current_datetime.month, current_datetime.day
    ) + timedelta(days=remaining_days)

    # Calculate the start datetime (end datetime - 1 month)
    start_datetime = end_datetime - timedelta(days=30)  # Assuming a month is 30 days

    # Calculate the period length in seconds
    period_length_seconds = (end_datetime - start_datetime).total_seconds()

    # Calculate the elapsed time in seconds
    elapsed_time_seconds = (current_datetime - start_datetime).total_seconds()

    # Calculate the percentage elapsed in the billing period
    percentage_elapsed = round((elapsed_time_seconds / period_length_seconds) * 100, 2)

    return percentage_elapsed


# Example usage:
remaining_days = 28  # Example number of remaining days in the billing period

percentage_elapsed = percentage_elapsed(remaining_days)
print("Percentage elapsed in the billing period:", percentage_elapsed)
