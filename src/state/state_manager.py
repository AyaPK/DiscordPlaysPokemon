import json
import os

def set_up_data():
    check_for_messages_json()

def check_for_messages_json():
    if not os.path.isfile('src/state/messages.json'):
        with open('src/state/messages.json', 'w') as file:
            json.dump({}, file)
