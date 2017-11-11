import sql_communicator
import logging

def change_list_to_string(data, field):
    """we really don't need this field, but record it somehow. Just in case"""
    if field in data:
        if data[field]:
            data[field] = str(data[field])
        else:
            data[field] = None

def save(data):
    """
    save json data to BD
    """
    (total_saved_bills, total_saved_sum, total_saved_items) = (0, 0, 0)
    
    main_key_order = set(data[0].keys())
    main_key_order.remove("items")
    main_key_order = list(main_key_order)
    items_key_order = set(data[0]["items"][0].keys())
    items_key_order = list(items_key_order)

    for bill in data:
        if sql_communicator.has_same_bill_record(bill):
            logging.info("the record is already in DB:\n" + str(bill))
            continue
        change_list_to_string(bill, "modifiers")
        change_list_to_string(bill, "stornoItems")
        vals = [bill[k] for k in main_key_order]
        new_id = sql_communicator.save_bill_to_DB(main_key_order, vals)
        total_saved_bills += 1
        total_saved_sum += bill["totalSum"]
        for item in bill["items"]:
            change_list_to_string(item, "modifiers")
            change_list_to_string(item, "storno")
            vals = [new_id]+[item[k] for k in items_key_order]
            sql_communicator.save_item_to_DB(items_key_order, vals)
            total_saved_items += 1
    sql_communicator.commit_changes()
    return (total_saved_bills, total_saved_sum, total_saved_items)
