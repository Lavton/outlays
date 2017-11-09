import config
import os
import pickle
import requests
import sys
import time
import uuid
from enum import Enum

_url_bot = "https://api.telegram.org/bot{}/".format(config.access_token)

def get_raw_updates():
    _last_date = 1510251396
    data_storage_pi = os.path.join(os.path.dirname(__file__), "data.pickle")
    if os.path.isfile(data_storage_pi):
        with open(data_storage_pi, "rb") as f:
            _last_date = pickle.load(f)
    response = requests.get(_url_bot + 'getUpdates')
    if response.status_code != 200:
        return False
    response = response.json()
    if not response["ok"]:
        return False
    for message in response["result"]:
        if "edited_message" in message:
            m = message["edited_message"]
        else:
            m = message["message"]
        if m["chat"]["username"] != config.username:
            continue
        if m['date'] < _last_date:
            continue
        else:
            _last_date = m["date"]
            with open(data_storage_pi, "wb") as f:
                pickle.dump(_last_date + 1, f)
            yield m
    _last_date += 1

class MessageType(Enum):
    JSON = 1
    TEXT = 2
    IMAGE = 3
    OTHER = 4

def get_message_type(message):
    if 'document' in message:
        if ".json" in message["document"]["file_name"]:
            return MessageType.JSON 
        # print(m_type)
    if 'photo' in message:
        return MessageType.IMAGE
    if 'text' in message:
        return MessageType.TEXT
    return MessageType.OTHER

def get_updates():
    for m in get_raw_updates():
        m_type = get_message_type(m)
        if m_type == MessageType.JSON:
            time.sleep(0.1)
            get_f_url = _url_bot + "getFile?file_id={}".format(m['document']['file_id'])
            response = requests.get(get_f_url)
            if response.status_code != 200:
                continue
            response = response.json()
            if not response["ok"]:
                continue
            response = response["result"]["file_path"]
            time.sleep(0.3)
            file_url = "https://api.telegram.org/file/bot{}/{}".format(config.access_token, response)
            response = requests.get(file_url)
            if response.status_code != 200:
                continue
            yield (MessageType.JSON, m['date'], response.json())
        if m_type == MessageType.TEXT:
           yield (MessageType.TEXT, m['date'], m['text']) 
        if m_type == MessageType.IMAGE:
            time.sleep(0.1)
            response = m['photo'][-1]['file_id']
            get_f_url = _url_bot + "getFile?file_id={}".format(response)
            response = requests.get(get_f_url)
            if response.status_code != 200:
                continue
            response = response.json()
            if not response["ok"]:
                continue
            response = response["result"]["file_path"]
            time.sleep(0.3)
            file_url = "https://api.telegram.org/file/bot{}/{}".format(config.access_token, response)
            r = requests.get(file_url, stream=True)
            file_name = "images/{}--{}.jpg".format(m["date"], uuid.uuid4())
            if r.status_code == 200:
                if not os.path.exists("images"):
                    os.makedirs("images")
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            else:
                continue
            yield (MessageType.IMAGE, m['date'], file_name) 

def send_message(message="Всё обработано"):
    requests.post(_url_bot + "sendMessage", data={"chat_id": config.user_id, "text":message})

if __name__ == '__main__':
    for m in get_updates():
        print(m)
        send_message()