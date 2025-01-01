#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import json

def _get_disk_usage():
    import psutil
    return psutil.disk_usage('/').percent

def _get_memory_usage():
    import psutil
    return psutil.virtual_memory().percent
def _get_cpu_usage():
    import psutil
    return psutil.cpu_percent(interval=1)
def _get_temperature():
    import psutil
    return psutil.sensors_temperatures()['coretemp'][0].current

def on_message(client, userdata, msg):
    print(msg.topic + "  " + str(msg.payload))

    if not msg.topic.endswith("get"):
           print("Incorrect command")
           return
    res = {"Disk usage": _get_disk_usage(),
        "Memory usage": _get_memory_usage(),
        "CPU usage": _get_cpu_usage(),
        "Temperature": _get_temperature(),
        "Power": 1}
    # Now we have the result, res, so send it back on the 'reply_to'
    # topic using the same correlation ID as the request.
    print("Sending response "+str(res))

    payload = json.dumps(res)
    client.publish("system/check/status", payload, qos=1)

def on_connect(client, userdata, flags, rc):
    client.subscribe("system/check/get")
    print("Subscribed to system/check/get")

def mqtt_system_controller():
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect

    # Uncomment to enable debug messages
    #mqttc.on_log = on_log

    mqttc.connect("localhost", 1883, 60)
    mqttc.loop_forever()

if __name__== '__main__':
    mqtt_system_controller()
