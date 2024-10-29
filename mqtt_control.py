#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A small example subscriber
"""
import paho.mqtt.client as paho
import json

sensors_params = {'0x00124b002916fe44' : {'name': 'Main door'}}

def on_device_message(mosq, obj, msg):
    #print("%-20s %d %s" % (msg.topic, msg.qos, msg.payload))
    #mosq.publish('pong', 'ack', 0)
    payload = json.loads(msg.payload.decode("utf-8"))
    print(json.dumps(payload, sort_keys=True, indent=4))
    for dev in payload:
        if dev["type"] == "EndDevice" and dev["disabled"] == False:
            #print(dev)
            endpoint = 'zigbee2mqtt/' + dev['friendly_name']
            obj['client'].subscribe(endpoint, 0)
            #print(endpoint)
            #obj['client'].message_callback_add(endpoint, on_motion_detector_message)
            #print(obj['client'])
            if dev["definition"]["description"] == "Motion sensor":
                obj['motion sensors'].append(endpoint)
            if dev["definition"]["description"] == "Temperature and humidity sensor":
                obj['temperature sensors'].append(endpoint)

def on_motion_detector_message(msg, cb):
    payload = json.loads(msg.payload.decode("utf-8"))
    device = msg.topic.split('/')[-1]
    name = device
    if device in sensors_params:
        if 'name' in sensors_params[device]:
            name = sensors_params[device]['name']

    if payload['occupancy'] == True:
        if payload['battery_low'] == True:
            battery = "Low"
        else:
            battery = "Full"
        cb("{}: motion detected, battery {}%".format(name, payload['battery']))

def on_temperature_message(msg, cb):
    payload = json.loads(msg.payload.decode("utf-8"))
    device = msg.topic.split('/')[-1]
    name = device
    if device in sensors_params:
        if 'name' in sensors_params[device]:
            name = sensors_params[device]['name']
 
    cb("{}: temperature {} humidity {}% battery {}%".format(name,
                                                            payload['temperature'],
                                                            payload['humidity'],
                                                            payload['battery']))
        
def on_message(mosq, obj, msg):
    if msg.topic in obj['motion sensors']:
        on_motion_detector_message(msg, obj["callback"])
    elif msg.topic in obj['temperature sensors']:
        on_temperature_message(msg, obj["callback"])
    else:
        print("Error: %-20s %d %s" % (msg.topic, msg.qos, msg.payload))

def on_publish(mosq, obj, mid):
    pass

def registry_device_message(ip, port, callback):
    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish
    context = {'client': client, 'motion sensors': [], 'temperature sensors':[], "callback":callback }
    client.user_data_set(context)
    #client.tls_set('root.ca', certfile='c1.crt', keyfile='c1.key')
    client.connect(ip, port, 60)

    client.subscribe("zigbee2mqtt/bridge/devices", 0)
    client.message_callback_add("zigbee2mqtt/bridge/devices", on_device_message)
    return context

def get_detailed_info(context):

    context["client"].publish('zigbee2mqtt/bridge/request/health_check', '{}')
    #client.publish('zigbee2mqtt/bridge/devices/get', '{"state": ""}')
    for m in context["motion sensors"]:
        print(m)
    for m in context["temperature sensors"]:
        print(m)
        #device = m.split('/')[-1]
        #client.publish(m + '/get', '{"state": ""}')
    
def mqtt_init(callback):
    context = registry_device_message("192.168.88.192", 1883, callback)
    #client = registry_device_message("localhost", 1883, callback)
    return context

def mqtt_run(context):
    context["client"].loop_forever()

def mqtt_print_cb(str):
    print(str)

if __name__ == '__main__':
    mqtt_init(mqtt_print_cb)
