import logging
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
    """
    get raw data from telegram as it is.
    yield only new messages, that comes from specific user
    """
    _last_date = 0
    if not config.debug_mode:
        data_storage_pi = os.path.join(os.path.dirname(__file__), "data.pickle")
        if os.path.isfile(data_storage_pi):
            with open(data_storage_pi, "rb") as f:
                _last_date = pickle.load(f)
    response = requests.get(_url_bot + 'getUpdates')
    if response.status_code != 200:
        logging.error("can't get the raw data!")
        return False
    response = response.json()
    if not response["ok"]:
        logging.error("can't get the raw data!")
        return False

    # getting data
    for message in response["result"]:
        if "edited_message" in message:
            m = message["edited_message"]
        else:
            m = message["message"]
        if m['date'] < _last_date:
            continue
        if m["chat"]["id"] != config.user_id:
            logging.warning("someone else take this bot: " + str(m["chat"]["username"]))
            continue
        else:
            logging.info("get new raw message\n" + str(message))
            _last_date = m["date"]
            if not config.debug_mode:
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
    """
    get type of the message
    """
    if 'document' in message:
        if ".json" in message["document"]["file_name"]:
            return MessageType.JSON 
    if 'photo' in message:
        return MessageType.IMAGE
    if 'text' in message:
        return MessageType.TEXT
    logging.warning("get other message type")
    return MessageType.OTHER

def get_file_on_id(file_id, stream=False):
    """
    return response of file
    """
    time.sleep(0.3)
    get_f_url = _url_bot + "getFile?file_id={}".format(file_id)
    response = requests.get(get_f_url)
    if response.status_code != 200:
        logging.error("can't get the file data!")
        return None
    response = response.json()
    if not response["ok"]:
        logging.error("can't get the file data!")
        return None
    response = response["result"]["file_path"]
    time.sleep(0.3)
    file_url = "https://api.telegram.org/file/bot{}/{}".format(config.access_token, response)
    return requests.get(file_url, stream=stream)



def get_updates():
    for m in get_raw_updates():
        m_type = get_message_type(m)
        logging.info("message type is " + str(m_type))
        if m_type == MessageType.JSON:
            response = get_file_on_id(m['document']['file_id'])
            if response.status_code != 200:
                logging.error("can't get the file data!")
                continue
            yield (MessageType.JSON, m['date'], response.json())
        if m_type == MessageType.TEXT:
           yield (MessageType.TEXT, m['date'], m['text']) 
        if m_type == MessageType.IMAGE:
            file_name = "images/{}--{}.jpg".format(m["date"], uuid.uuid4())
            r = get_file_on_id(m['photo'][-1]['file_id'], True)
            if r.status_code == 200:
                if not os.path.exists("images"):
                    os.makedirs("images")
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            else:
                logging.error("can't get the file data!")
                continue
            yield (MessageType.IMAGE, m['date'], file_name) 

def send_message(message="Всё обработано"):
    requests.post(_url_bot + "sendMessage", data={"chat_id": config.user_id, "text": message})

if __name__ == '__main__':
    for m in get_updates():
        print(m)
        send_message()