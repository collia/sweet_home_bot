#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import json
import sched, time

def on_message(client, userdata, msg):
    print(msg.topic + "  " + str(msg.payload))

def on_connect(client, userdata, flags, rc):
    client.subscribe("system/check/#")
    print("Subscribed to system/check/#")

def on_log(client, userdata, level, buf):
    print("log: ",buf)

def mqtt_system_controller():
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect

    # Uncomment to enable debug messages
    mqttc.on_log = on_log

    mqttc.connect("localhost", 1883, 60)
    #mqttc.loop_forever()
    #mqttc.subscribe("system/check/#")
    mqttc.loop_start()
    return mqttc

def sheadule_check_event(mqttc, scheduler):
    print("Sending check request")
    mqttc.publish("system/check/get", "get", qos=1)
    # Reschedule the event
    scheduler.enter(6, 1, sheadule_check_event, argument=(mqttc, scheduler))

def sheadule_check(mqttc):
    '''periodically send the messages to the system checker'''
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(1, 1, sheadule_check_event, argument=(mqttc, scheduler))
    scheduler.run()


if __name__== '__main__':
    mqttc = mqtt_system_controller()
    sheadule_check(mqttc)
