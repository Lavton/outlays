import datetime

d = datetime.datetime.today()
def get_begin_of_day():
    return d.date()

def get_begin_of_week():
    return (d - datetime.timedelta(days=d.weekday())).date()

def get_begin_of_month():
    return (d - datetime.timedelta(days=d.day - 1)).date()

def get_begin_of_prev_month():
    lm = d - datetime.timedelta(days=d.day - 1)
    r = datetime.date(lm.year + (0 if lm.month != 1 else -1), (lm.month-2)%12+1, lm.day)
    return r

def get_timestamp_from_date(date):
    return int((date- datetime.datetime(1970, 1, 1).date()) / datetime.timedelta(seconds=1))