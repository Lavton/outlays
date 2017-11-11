import datetime

d = datetime.datetime.today()
def get_begin_of_day():
    return d.date()

def get_begin_of_week():
    return (d - datetime.timedelta(days=d.weekday())).date()

def get_begin_of_month():
    return (d - datetime.timedelta(days=d.day - 1)).date()

def get_timestamp_from_date(date):
    return int((date- datetime.datetime(1970, 1, 1).date()) / datetime.timedelta(seconds=1))