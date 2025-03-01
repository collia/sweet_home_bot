from collections import deque
from datetime import datetime, timedelta
from dateutil import parser
import json
import os
import matplotlib.pyplot as plt
import matplotlib
import io

matplotlib.use('Agg')  # Use a non-GUI backend

buffer = {}
BUFFER_MAX_LEN = 1000
FILE = 'config/statistic.json'

def statistic_init():
    upload_from_file(FILE)
def statistic_append(dev:str, record):
    if not dev in buffer:
        buffer[dev] = deque(maxlen=BUFFER_MAX_LEN)
    buffer[dev].append((datetime.now(), record))
    store_in_json_file(FILE)
    #print(buffer)

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


def get_statistic_graph(dev_id, fields, days, title):
    # Current time and 24-hour window
    now = datetime.now()
    days_ago = now - timedelta(days=days)

    # Filter data for the last 24 hours
    filtered_data = [(timestamp, data) for timestamp, data in buffer[dev_id] if timestamp > days_ago]

    # Ensure there's data to plot
    if not filtered_data:
        print(f"No data available for the past {days} days.")
    else:
        # Extract data from filtered buffer
        timestamps = [entry[0] for entry in filtered_data]
        data = {}
        for field in fields:
            print(filtered_data)
            #data[field[0]] = [entry[1][field[0]] for entry in filtered_data]
            result = []
            for entry in filtered_data:
                if field[0] in entry[1]:
                    result.append(entry[1][field[0]])
                else:
                    print(f'Error: {field[0]} not in {entry[1]}')
                    result.append(0)
            data[field[0]] = result


    # Plotting
    #plt.figure(figsize=(10, 6))
    #for field in fields:
    #    plt.plot(timestamps, data[field], label=field, marker='o', linestyle='-')


    # Formatting the graph
    #plt.title(f"Device Statistics Over Last {days} days", fontsize=16)
    #plt.xlabel("Time", fontsize=12)
    #plt.ylabel("Value", fontsize=12)
    #plt.legend(loc="upper right", fontsize=10)
    #plt.grid(True, linestyle='--', alpha=0.7)
    #plt.xticks(rotation=45)
    #plt.tight_layout()

    # Create the figure and the first axis
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot temperature on the first Y-axis
    ax1.plot(timestamps, data[fields[0][0]], 'r-o', label=fields[0][1])
    ax1.set_xlabel("Time")
    ax1.set_ylabel(fields[0][1], color="red")
    ax1.tick_params(axis="y", labelcolor="red")
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Create a second Y-axis for humidity
    ax2 = ax1.twinx()
    ax2.plot(timestamps, data[fields[1][0]], 'b-s', label=fields[1][1])
    ax2.set_ylabel(fields[1][1], color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")

    # Title and legend
    plt.title(title)
    fig.tight_layout()

    # Save the plot to an in-memory buffer
    image_buffer = io.BytesIO()
    plt.savefig(image_buffer, format="jpg", dpi=300)
    image_buffer.seek(0)  # Rewind the buffer for reading
    return image_buffer
