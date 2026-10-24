import json
import os

INPUTS_FILE = 'src/state/inputs.txt'
VOTES_FILE = 'src/state/votes.json'
MESSAGES_FILE = 'src/state/messages.json'


def set_up_data():
    check_for_messages_json()
    check_for_inputs_txt()
    check_for_votes_json()


def check_for_messages_json():
    if not os.path.isfile(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'w') as file:
            json.dump({}, file)


def check_for_inputs_txt():
    if not os.path.isfile(INPUTS_FILE):
        open(INPUTS_FILE, 'w').close()


def check_for_votes_json():
    if not os.path.isfile(VOTES_FILE):
        with open(VOTES_FILE, 'w') as file:
            json.dump({}, file)


def record_input(input_name: str):
    with open(INPUTS_FILE, 'a') as file:
        file.write(input_name + '\n')


def record_votes(voter_ids: list[int]):
    if not voter_ids:
        return
    with open(VOTES_FILE, 'r') as file:
        votes = json.load(file)
    for uid in voter_ids:
        key = str(uid)
        votes[key] = votes.get(key, 0) + 1
    with open(VOTES_FILE, 'w') as file:
        json.dump(votes, file, indent=2)