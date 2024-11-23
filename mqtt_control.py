#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as paho
import json


_devices = []

def on_device_message(mosq, obj, msg):
    global _devices
    _devices = []
    payload = json.loads(msg.payload.decode("utf-8"))
    print(json.dumps(payload, sort_keys=True, indent=4))
    for dev in payload:
        if dev["type"] == "EndDevice" and dev["disabled"] == False:
            #print(dev)
            _devices.append(dev)
            endpoint = 'zigbee2mqtt/' + dev['friendly_name']
            obj['client'].subscribe(endpoint, 0)
    obj['device callback'](_generate_device_tree(payload))

def get_devices_list():
    return [dev['friendly_name'] for dev in _devices]

def _generate_device_tree(msg):
    return msg

def on_message(mosq, obj, msg):
    device = msg.topic.split('/')[-1]
    payload = json.loads(msg.payload.decode("utf-8"))
    obj["callback"](device, payload)

def on_publish(mosq, obj, mid):
    pass

def registry_device_message(ip, port, callback, device_callback):
    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish
    context = {'client': client, "callback":callback, "device callback":device_callback }
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

def mqtt_init(ip, port, callback, device_callback):
    context = registry_device_message(ip, port, callback, device_callback)
    return context

def mqtt_run(context):
    context["client"].loop_forever()

def mqtt_print_cb(str):
    print(str)

if __name__ == '__main__':
    mqtt_init(mqtt_print_cb)
