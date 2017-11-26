import sql_communicator
import config
import os
import distance
import pickle


def get_shop_bills():
    # get data
    _last_date = 0
    if not config.debug_mode:
        data_storage_pi = os.path.join(os.path.dirname(__file__), "data_beaut_sh.pickle")
        if os.path.isfile(data_storage_pi):
            with open(data_storage_pi, "rb") as f:
                _last_date = pickle.load(f)
    raw_bills = sql_communicator.get_raw_shops(_last_date)

    # struct data
    raw_bills = [{"id": i[0], "name": i[1], "inn": i[2], "totalSum": i[3], "dateTime": int(i[4])} for i in raw_bills]

    # clear data
    for shop in raw_bills:
        if shop["name"]:
            shop["name"] = shop["name"].lower().strip() # lower etc
        if shop["inn"]:
            shop["inn"] = int(shop["inn"])

    # remove 'зао' etc and "рога и копыта" -> рога и копыта
    rubbish_words = ["зао", "ооо", "ип", "общество с ограниченной ответственностью", "ао"]
    for shop in raw_bills:
        if shop["name"]:
            for w in rubbish_words:
                if shop["name"].startswith(w):
                    shop["name"] = shop["name"][len(w):].strip()
                    break
            if (shop["name"][0] == shop["name"][-1] == '"') or (shop["name"][0] == shop["name"][-1] == "'"):
                shop["name"] = shop["name"][1:-1]
    return raw_bills

def is_same_group_on_inn(inn1, inn2):
    "группировка по ИНН"
    if inn1 and inn2:
        return inn1 == inn2
    else:
        return False

def is_same_group_on_name(name1, name2):
    "группировка по имени"
    if name1 and name2:
        if name1 == name2:
            return True
        else:
            return False
    else:
        return False

def groupirize(bills):
    "группируем чеки по магазинам"
    groups = []
    for bill in bills:
        if bill["inn"]:
            for group in groups:
                if is_same_group_on_inn(group[0]["inn"], bill["inn"]):
                    group.append(bill)
                    break
            else:
                groups.append([bill])
    for bill in bills:
        if not bill["inn"]:
            for group in groups:
                if is_same_group_on_name(group[0]["name"], bill["name"]):
                    group.append(bill)
                    break
            else:
                groups.append([bill])
    return groups

def find_throw_canonic(shop_name, all_known_shops):
    candidates = []
    if not shop_name:
        return candidates
    for i in range(len(all_known_shops)):
        shps = all_known_shops[i][1].lower()
        if shps == shop_name:
            candidates.append((i, shps))
        # полное название и часть этого полного названия
        if shop_name in shps:
            candidates.append((i, shps))
        if shps in shop_name:
            candidates.append((i, shps))
        # опечатка в полном названии
        if len(shps) - 2 <= len(shop_name) <= len(shps) + 2:
            if distance.levenshtein(shps, shop_name) <= 2:
                candidates.append((i, shps))

    # только уникальные собираем
    used = set()
    unique = [x for x in candidates if x not in used and (used.add(x) or True)]
    unique.append((-1, shop_name))
    return [(i, c.title()) for (i, c) in unique if c]

def write_new_beautiful_bill(bill, canon_shop):
    return sql_communicator.write_beatiful_bill(bill["id"], bill["totalSum"], canon_shop[1], canon_shop[0], bill["dateTime"])


def set_last_data(_last_date):
    data_storage_pi = os.path.join(os.path.dirname(__file__), "data_beaut_sh.pickle")
    if not config.debug_mode:
        with open(data_storage_pi, "wb") as f:
            pickle.dump(_last_date + 1, f)