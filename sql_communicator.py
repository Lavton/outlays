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

cursor.execute("""CREATE TABLE IF NOT EXISTS CanonShopsNames(
        id INTEGER primary key autoincrement, 
        shop_name TEXT,
        shop_short_descript TEXT NULL
    );"""
)

cursor.execute("""CREATE TABLE IF NOT EXISTS CanonRawShopsConnect(
        id INTEGER primary key autoincrement, 
        shop_id INTEGER,
        user TEXT NULL,
        userInn TEXT NULL,
        FOREIGN KEY(shop_id) REFERENCES CanonShopsNames(id)
    );"""
)


cursor.execute("""CREATE TABLE IF NOT EXISTS BeatifyBillMain(
        id INTEGER primary key, 
        totalSum INTEGER NULL,
        shop_name TEXT NULL,
        shop_id INTEGER NULL,
        dateTime INTEGER NULL,
        FOREIGN KEY(id) REFERENCES RawBillMain(id),
        FOREIGN KEY(shop_name) REFERENCES CanonShopsNames(shop_name),
        FOREIGN KEY(shop_id) REFERENCES CanonShopsNames(id)
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

def get_summary_from_date(timestamp, limit=10):
    summary = cursor.execute(
        "SELECT sum(totalSum)/100, shop_name FROM BeatifyBillMain WHERE dateTime>? GROUP BY shop_id ORDER BY sum(totalSum) DESC LIMIT ?",
        (timestamp, limit)
    ).fetchall()
    return summary

def get_raw_shops(timestamp):
    return cursor.execute(
        "SELECT id, user, userInn, totalSum, dateTime FROM RawBillMain WHERE dateTime>?",
        (timestamp, )
    ).fetchall()


def commit_changes():
    connection.commit()

def find_shop_on_inn(inn):
    shops_id = cursor.execute(
        "SELECT shop_id FROM CanonRawShopsConnect WHERE userInn=?",
        (inn, )
    ).fetchall()
    return shops_id

def find_shop_on_name(user):
    shops_id = cursor.execute(
        "SELECT shop_id FROM CanonRawShopsConnect WHERE user=?",
        (user, )
    ).fetchall()
    return shops_id

def get_all_canonic_shops():
    return cursor.execute(
        "SELECT id, shop_name, shop_short_descript FROM CanonShopsNames"
    ).fetchall()

def find_products_on_bill_id(bill_id):
    return cursor.execute(
        "SELECT name FROM RawBillItems WHERE bill_id=?",
        (bill_id, )
    ).fetchall()

def write_new_synonim(shop_id, user, userInn):
    exe_str = "INSERT OR REPLACE INTO CanonRawShopsConnect (shop_id,user,userInn) VALUES (?,?,?);"
    cursor.execute(exe_str, (shop_id, user, userInn))

def write_new_canon_shop(shop_name, shop_descipt):
    exe_str = "INSERT OR REPLACE INTO CanonShopsNames (shop_name,shop_short_descript) VALUES (?,?);"
    cursor.execute(exe_str, (shop_name, shop_descipt))
    return cursor.lastrowid

def write_beatiful_bill(id, totalSum, shop_name, shop_id, dateTime):
    # чек что не существует чек
    if bool(len(
            cursor.execute(
                "SELECT 1 FROM BeatifyBillMain WHERE id=?",
                 (id,)).fetchall()
        )):
        return 0
    exe_str = "INSERT OR REPLACE INTO BeatifyBillMain (id,totalSum,shop_name,shop_id,dateTime) VALUES (?,?,?,?,?);"
    cursor.execute(exe_str, (id, totalSum, shop_name, shop_id, dateTime))
    return cursor.lastrowid    
