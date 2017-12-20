import beatify_shops_model
import sql_communicator

bills = beatify_shops_model.get_shop_bills()
last_data = max([b["dateTime"] for b in bills], default=0)
groups = beatify_shops_model.groupirize(bills)
all_known_shops = sql_communicator.get_all_canonic_shops()

def write_old_shop(canon_shop, user, userInn):
    print("Write old", canon_shop)
    sql_communicator.write_new_synonim(canon_shop[0], user, userInn)

def check_double_if_new(name):
    name = name.lower()
    cands = beatify_shops_model.find_throw_canonic(name, all_known_shops)
    if len(cands) == 1: 
        return -46
    else: 
        ans = input("Это название похоже на {}. Это оно? [Y/n]".format(cands[0][1]))
        if not ans:
            ans = "Y"
        ans = ans.lower()
        if ans=="y":
            return cands[0][0]
        else:
            return -46

def checks_new_etc(name, group):
    g = group[0]
    check = check_double_if_new(name)
    print("check", check)
    if check != -46:
        write_old_shop(all_known_shops[check], g["name"], g["inn"])
        return check
    else:
        print("Aaaa")
        all_known_shops.append(write_new_shop(name, g["name"], g["inn"]))
        return len(all_known_shops) - 1

def write_new_shop(name, user, userInn):
    print("Write new", name)
    des = input("краткое описание: ").strip()
    new_shop_id = sql_communicator.write_new_canon_shop(name.strip(), des)
    sql_communicator.write_new_synonim(new_shop_id, user, userInn)
    return (new_shop_id, name, des)

for group in groups:
    print(group[0])
    conn_shop_ids = []
    if group[0]["inn"]:
        conn_shop_ids = sql_communicator.find_shop_on_inn(group[0]["inn"])
    elif group[0]["name"]:
        conn_shop_ids = sql_communicator.find_shop_on_name(group[0]["name"])
    if conn_shop_ids: # уже есть данный магазин
        for i in range(len(all_known_shops)):
            if int(conn_shop_ids[0][0]) == int(all_known_shops[i][0]):
                number_in_canon = i
                break
        pass
    else:
        candidates = beatify_shops_model.find_throw_canonic(group[0]["name"], all_known_shops)
        print("последние товары в этом магазине: ", sql_communicator.find_products_on_bill_id(group[-1]["id"]))
        c_shop = input("Название магазина: {} [0]: ".format(", ".join([
            "{} '{}'".format(i, candidates[i][1]) for i in range(len(candidates))
        ])))
        if not c_shop:
            c_shop = "0"
        is_new = False
        try: 
            c_shop = int(c_shop)
            if c_shop == len(candidates) - 1:
                number_in_canon = checks_new_etc(candidates[-1][1], group)
            else:
                g = group[0]
                number_in_canon = candidates[c_shop][0]
                write_old_shop(all_known_shops[number_in_canon], g["name"], g["inn"]) # уже есть такой магазин
                
        except ValueError:
            number_in_canon = checks_new_etc(c_shop, group)
    for g in group:
        beatify_shops_model.write_new_beautiful_bill(g, all_known_shops[number_in_canon])
    sql_communicator.commit_changes()

beatify_shops_model.set_last_data(last_data)