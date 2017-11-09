import sqlite3

conn = sqlite3.connect('outlay.db')
cursor = conn.cursor()
# cursor.execute("""CREATE TABLE IF NOT EXISTS RawBillMain(
#         id INTEGER primary key autoincrement, 
#         totalSum INTEGER NULL,
#         user TEXT NULL,
#         dateTime INTEGER NULL
#     );"""
# )
# cursor.execute("""CREATE TABLE IF NOT EXISTS RawBillItems(
#         id INTEGER primary key autoincrement, 
#         bill_id INTEGER,
#         name TEXT NULL,
#         sum INTEGER NULL,
#         FOREIGN KEY(bill_id) REFERENCES RawBillMain(id)
#     );"""
# )



def save(date, message):
    (totalSavedMain, totalSavedSum, totalSavedItems) = (0, 0, 0)
    message = message.strip()
    lines = message.split("\n")
    if len(lines) == 1:
        return (totalSavedMain, totalSavedSum, totalSavedItems)

    shop_name = lines[0]
    totalSum = 0
    for line in lines[1:]:
        [price, good] = line.split(" ", 1)
        try:
            price = float(price)
        except ValueError as e:
            continue
        totalSum += price * 100
    exe_str = "INSERT OR REPLACE INTO RawBillMain (totalSum, user, dateTime, operator) VALUES (?,?,?,?);"
    cursor.execute(exe_str, (totalSum, shop_name, date, "FROM TEXT"))
    new_id = cursor.lastrowid
    totalSavedMain += 1
    totalSavedSum += totalSum
    for line in lines[1:]:
        [price, good] = line.split(" ", 1)
        try:
            price = float(price)
        except ValueError as e:
            continue
        price = int(price * 100)
        exe_str = "INSERT OR REPLACE INTO RawBillItems (bill_id, name, sum) VALUES (?,?,?);"
        cursor.execute(exe_str, (new_id, good, price))
        totalSavedItems += 1

    conn.commit()
    return (totalSavedMain, totalSavedSum, totalSavedItems)