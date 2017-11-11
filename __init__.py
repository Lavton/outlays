import logging
import time
import os
logging.basicConfig(format=u'[%(asctime)s] %(filename)s[LINE:%(lineno)d, FUNC:%(funcName)s]# %(levelname)-8s  %(message)s', 
    level=logging.INFO, filename=os.path.join(os.path.dirname(__file__), "main.log"))

import telegram_communicator
from telegram_communicator import MessageType
import json_worker
import text_worker
import timey_wimey
import sql_communicator
import config

# we send statistic to the user at the end
(total_saved_bills, total_saved_sum, total_saved_items) = (0, 0, 0)
for m_type, m_date, message in telegram_communicator.get_updates():
    res = (0, 0, 0)
    if m_type == MessageType.JSON:
        res = json_worker.save(message)
    if m_type == MessageType.TEXT:
        res = text_worker.save(m_date, message)

    total_saved_bills += res[0]
    total_saved_sum += res[1]
    total_saved_items += res[2]
    print(m_type)

if total_saved_bills:
    today_sum = sql_communicator.get_total_sum_from_date(
        timey_wimey.get_timestamp_from_date(
            timey_wimey.get_begin_of_day()
    ))
    week_sum = sql_communicator.get_total_sum_from_date(
        timey_wimey.get_timestamp_from_date(
            timey_wimey.get_begin_of_week()
    ))

    month_sum = sql_communicator.get_total_sum_from_date(
        timey_wimey.get_timestamp_from_date(
            timey_wimey.get_begin_of_month()
    ))

    if config.debug_mode:
        telegram_communicator.send_message("DEBUG MODE")
        time.sleep(0.5)
    telegram_communicator.send_message("""Обработано новых чеков: {} 
на сумму {} 
(наименований - {} шт.)
____________
с начала дня: {}
с начала недели: {}
с начала месяца: {}
""".format(total_saved_bills, total_saved_sum//100, total_saved_items, today_sum, week_sum, month_sum))