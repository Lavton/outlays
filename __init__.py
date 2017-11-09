import telegram_communicator
from telegram_communicator import MessageType
import json_worker
import text_worker
import datetime
import sqlite3

(totalSavedMain, totalSavedSum, totalSavedItems) = (0, 0, 0)
for m_type, m_date, message in telegram_communicator.get_updates():
    res = (0, 0, 0)
    if m_type == MessageType.JSON:
        res = json_worker.save(message)
    if m_type == MessageType.TEXT:
        res = text_worker.save(m_date, message)

    totalSavedMain += res[0]
    totalSavedSum += res[1]
    totalSavedItems += res[2]
    print (m_type)

if totalSavedMain:
    d = datetime.datetime.today()
    start_of_week = (d - datetime.timedelta(days=d.weekday())).date()
    start_of_day = d.date()
    day_timestamp = int((start_of_day - datetime.datetime(1970, 1, 1).date()) / datetime.timedelta(seconds=1))
    week_timestamp = int((start_of_week - datetime.datetime(1970, 1, 1).date()) / datetime.timedelta(seconds=1))
    conn = sqlite3.connect('outlay.db')
    cursor = conn.cursor()
    today_sum = cursor.execute(
        "SELECT sum(totalSum) FROM RawBillMain WHERE dateTime>?",
        (day_timestamp, )
    ).fetchone()
    if not today_sum:
        today_sum = (0, )
    today_sum = today_sum[0] / 100
    week_sum = cursor.execute(
        "SELECT sum(totalSum) FROM RawBillMain WHERE dateTime>?",
        (week_timestamp, )
    ).fetchone()
    
    if not week_sum:
        week_sum = (0, )
    week_sum = week_sum[0] / 100

    telegram_communicator.send_message("""Обработано новых чеков: {} 
на сумму {} 
(наименований - {} шт.)
____________
всего за день: {}
с начала недели: {}
""".format(totalSavedMain, totalSavedSum//100, totalSavedItems, today_sum, week_sum))