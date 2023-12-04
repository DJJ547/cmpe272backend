from datetime import datetime

def check_most_recent_title(title_data):
    print(title_data)
    for title in title_data:
        if title[3] == datetime(9999, 1, 1):
            return title
    return title[3]