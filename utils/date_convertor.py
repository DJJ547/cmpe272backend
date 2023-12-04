from datetime import datetime
from datetime import timedelta

def convert_datetime_to_string(dtime):
    if not dtime:
        return None
    dstring = ''
    if isinstance(dtime, datetime):
        dstring = dtime.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(dtime, timedelta):
        dstring = str(dtime)
    return dstring

def convert_string_to_datetime(dstring, dtype):
    if not dstring:
        return None
    dtime = None
    if dtype == 'datetime':
        dtime = datetime.strptime(dstring, '%Y-%m-%d %H:%M:%S')
    elif dtype == 'timedelta':
        dtime = datetime.strptime(dstring, '%H:%M:%S')
        dtime = timedelta(hours=dtime.hour, minutes=dtime.minute, seconds=dtime.second)
    return dtime

def datetime_to_eight_hour_before(input):

    # Convert string to datetime object (assuming the input string is in ISO 8601 format)
    input_datetime = datetime.fromisoformat(input[:-1])  # Removing the 'Z' at the end

    # Subtract 8 hours
    adjusted_datetime = input_datetime - timedelta(hours=8)

    # Format the adjusted datetime as a string
    formatted_time_string = adjusted_datetime.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_time_string