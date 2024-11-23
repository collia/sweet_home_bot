from collections import deque
from datetime import datetime
from dateutil import parser
import json
import os

buffer = {}
BUFFER_MAX_LEN = 1000
FILE = 'statistic.json'

def statistic_init():
    upload_from_file(FILE)
def statistic_append(dev:str, record):
    if not dev in buffer:
        buffer[dev] = deque(maxlen=BUFFER_MAX_LEN)
    buffer[dev].append((datetime.now(), record))
    store_in_json_file(FILE)

def statisctic_get_last_record(dev:str):
    if not dev in buffer:
        return None
    return buffer[dev][-1]

def store_in_json_file(file_path: str):
    """
    Serialize the buffer and store it in a JSON file.
    """
    # Convert buffer to JSON-serializable format
    serializable_buffer = {
        dev: [(timestamp.isoformat(), rec) for timestamp, rec in records]
        for dev, records in buffer.items()
    }
    # Write to file
    with open(file_path, "w") as file:
        json.dump(serializable_buffer, file, indent=4)

def upload_from_file(file_path: str):
    """
    Load the buffer from a JSON file.
    """
    global buffer  # To modify the global buffer
    if not os.path.exists(file_path):
        print(f"File '{file_path}' does not exist. Buffer remains empty.")
        store_in_json_file(file_path)
    with open(file_path, "r") as file:
        data = json.load(file)
        buffer = {
            dev: deque(
                [(datetime.fromisoformat(timestamp), rec) for timestamp, rec in records],
                maxlen=BUFFER_MAX_LEN
            )
            for dev, records in data.items()
        }

