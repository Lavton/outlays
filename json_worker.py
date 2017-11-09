import sqlite3

conn = sqlite3.connect('outlay.db')
cursor = conn.cursor()
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

def save(data):
    (totalSavedMain, totalSavedSum, totalSavedItems) = (0, 0, 0)
    main_key_order = set(data[0].keys())
    main_key_order.remove("items")
    main_key_order = list(main_key_order)

    items_key_order = set(data[0]["items"][0].keys())
    items_key_order = list(items_key_order)
    exe_str = "INSERT OR REPLACE INTO RawBillMain ({cols}) VALUES (" + "?,"*(len(main_key_order)-1) + "?);"
    exe_str_items = "INSERT OR REPLACE INTO RawBillItems (bill_id, {cols}) VALUES (" + "?,"*(len(items_key_order)) + "?);"
    for bill in data:
        if len(
            cursor.execute(
                "SELECT 1 FROM RawBillMain WHERE totalSum=? AND dateTime=?",
                 (bill["totalSum"] , bill["dateTime"])).fetchall()
        ):
            continue
        if bill["modifiers"]:
            bill["modifiers"] == str(bill["modifiers"])
        else:
            bill["modifiers"] = None
        if bill["stornoItems"]:
            bill["stornoItems"] == str(bill["stornoItems"])
        else:
            bill["stornoItems"] = None
        vals = [bill[k] for k in main_key_order]
        cursor.execute(exe_str.format(cols=", ".join(main_key_order)), vals)
        new_id = cursor.lastrowid
        totalSavedMain += 1
        totalSavedSum += bill["totalSum"]
        for item in bill["items"]:
            if item["modifiers"]:
                item["modifiers"] == str(item["modifiers"])
            else:
                item["modifiers"] = None
            if item["storno"]:
                item["storno"] == str(item["storno"])
            else:
                item["storno"] = None
            vals = [new_id]+[item[k] for k in items_key_order]
            cursor.execute(exe_str_items.format(cols=", ".join(items_key_order)), vals)
            totalSavedItems += 1
    conn.commit()
    return (totalSavedMain, totalSavedSum, totalSavedItems)
