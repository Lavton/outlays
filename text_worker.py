import sql_communicator
import logging



def save(date, message):
    """
    save info from message in DB with datetime=`date`
    message should be like:

    shop_name
    sum1 item1
    sum2 item2

    or for unimportnant - just `sum`
    """
    (total_saved_bills, total_saved_sum, total_saved_items) = (0, 0, 0)
    message = message.strip()
    lines = message.split("\n")
    if len(lines) == 1:
        try:
            price = float(lines[0])
            message = "{}\n{} {}".format("Неважно", price, "Неважно")
            lines = message.split("\n")
        except ValueError as e:
            logging.info("this is not record: " + str(message))
            return (total_saved_bills, total_saved_sum, total_saved_items)

    shop_name = lines[0]
    total_sum = 0
    for line in lines[1:]:
        [price, good] = line.split(" ", 1)
        try:
            price = float(price)
        except ValueError as e:
            continue
        total_sum += price * 100
    new_id = sql_communicator.save_bill_to_DB(["totalSum", "user", "dateTime", "operator"], (total_sum, shop_name, date, "FROM TEXT"))
    total_saved_bills += 1
    total_saved_sum += total_sum
    for line in lines[1:]:
        [price, good] = line.split(" ", 1)
        try:
            price = float(price)
        except ValueError as e:
            continue
        price = int(price * 100)
        sql_communicator.save_item_to_DB(["name", "sum"], (new_id, good, price))
        total_saved_items += 1

    sql_communicator.commit_changes()
    return (total_saved_bills, total_saved_sum, total_saved_items)