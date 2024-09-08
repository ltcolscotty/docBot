import datetime


def get_time_info():

    today = datetime.datetime.now()

    if (today.month == 12) or (today.month <= 2):
        quarter = "Winter"
    elif today.month <= 5:
        quarter = "Spring"
    elif today.month <= 8:
        quarter = "Summer"
    else:
        quarter = "Autumn"
    return [quarter, today.year]
