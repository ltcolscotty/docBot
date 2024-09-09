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
        quarter = "Fall"
    return [quarter, today.year]


def make_file_name():
    date_list = get_time_info()
    return f"BM Transparency Report: {date_list[0]} Quarter {date_list[1]}"
