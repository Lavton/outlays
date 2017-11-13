import os
import sqlite3
import logging
import config

db_name = os.path.join(os.path.dirname(__file__), config.db_name)
connection = sqlite3.connect(db_name)
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS RawBillMain(
        id INTEGER primary key autoincrement, 
        kktNumber TEXT NULL,
        stornoItems TEXT NULL,
        fiscalSign TEXT NULL,
        userInn TEXT NULL,
        cashTotalSum INTEGER NULL,
        nds0 TEXT NULL, 
        totalSum INTEGER NULL,
        taxationType TEXT NULL,
        fiscalDriveNumber INTEGER NULL,
        nds18 INTEGER NULL,
        kktRegId TEXT NULL,
        user TEXT NULL,
        ndsCalculated10 TEXT NULL,
        operationType TEXT NULL,
        markup TEXT NULL,
        fiscalDocumentNumber TEXT NULL,
        ecashTotalSum INTEGER NULL,
        nds10 INTEGER NULL,
        dateTime INTEGER NULL,
        markupSum TEXT NULL,
        retailPlaceAddress TEXT NULL,
        modifiers TEXT NULL,
        ndsNo TEXT NULL,
        requestNumber INTEGER NULL,
        discountSum INTEGER NULL,
        shiftNumber INTEGER NULL,
        ndsCalculated18 TEXT NULL,
        operator TEXT NULL,
        discount TEXT NULL
    );"""
)
cursor.execute("""CREATE TABLE IF NOT EXISTS RawBillItems(
        id INTEGER primary key autoincrement, 
        bill_id INTEGER,
        ndsCalculated10 TEXT NULL,
        quantity REAL NULL,
        name TEXT NULL,
        nds18 TEXT NULL,
        ndsCalculated18 TEXT NULL,
        price INTEGER NULL,
        storno TEXT NULL,
        nds10 TEXT NULL,
        sum INTEGER NULL,
        ndsNo TEXT NULL,
        nds0 TEXT NULL,
        modifiers TEXT NULL,
        FOREIGN KEY(bill_id) REFERENCES RawBillMain(id)
    );"""
)
connection.commit()

def has_same_bill_record(bill):
    return bool(len(
            cursor.execute(
                "SELECT 1 FROM RawBillMain WHERE totalSum=? AND dateTime=?",
                 (bill["totalSum"] , bill["dateTime"])).fetchall()
        ))

def save_bill_to_DB(cols, vals):
    exe_str = "INSERT OR REPLACE INTO RawBillMain ({cols}) VALUES (" + "?,"*(len(cols)-1) + "?);"
    cursor.execute(exe_str.format(cols=", ".join(cols)), vals)
    return cursor.lastrowid

def save_item_to_DB(cols, vals):
    exe_str = "INSERT OR REPLACE INTO RawBillItems (bill_id, {cols}) VALUES (" + "?,"*(len(cols)) + "?);"
    cursor.execute(exe_str.format(cols=", ".join(cols)), vals)

def get_total_sum_from_date(timestamp):
    my_sum = cursor.execute(
        "SELECT sum(totalSum) FROM RawBillMain WHERE dateTime>?",
        (timestamp, )
    ).fetchone()
    if not my_sum[0]:
        my_sum = (0, )
    my_sum = my_sum[0] / 100
    return my_sum

def commit_changes():
    connection.commit()