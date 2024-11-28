#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mqtt_control
import telegram_bot
import mqtt_statistic
import json
import math

class Configuration:
    settings_file = 'config.json'
    settings = {}
    def __init__(self):
        self.read_settings()
        #print(self.settings['Telegram']['Bot token'])
        if not self._check_settings():
            fail(1)

    def write_settings(self):
        js = json.loads('''
{
  "Telegram": {
    "Bot token": "Bot",
    "White list":
      {
        "User": {
          "Allowed": true,
          "Subscribed": true
        }
      }
  },
  "ZigBee": {
    "Devices": [
      {
        "0x00124b002916fe44": {
          "name": "Main door"
        }
      }
    ]
  }
  "mqtt": {
        "ip":"192.168.88.192",
        "port":1883
  }
}
''')
        with open(self.settings_file, 'w', encoding="utf-8") as f:
            json.dump(self.settings, f, sort_keys=True, indent=4)
    def read_settings(self):
        with open(self.settings_file, 'r', encoding="utf-8") as f:
            self.settings = json.load(f)
            #print(self.settings)
    def _check_settings(self):
        '''TODO extend errors'''
        if self.settings['Telegram']['Bot token'] == '':
            return False
        return True

    def get_telegram_token(self):
        return self.settings['Telegram']['Bot token']

    def get_telegram_user_info(self, user: str):
        if user in self.settings['Telegram']['White list']:
            return (self.settings['Telegram']['White list'][user]['Allowed'],
                    self.settings['Telegram']['White list'][user]['Subscribed'])
        else:
            return (False, False)

    def set_telegram_user_info(self, user: str, subscribed:bool):
        if user in self.settings['Telegram']['White list']:
            self.settings['Telegram']['White list'][user]['Subscribed'] = subscribed

    def get_telegram_subscribed_users(self):
        res = []
        for user in self.settings['Telegram']['White list']:
            if self.settings['Telegram']['White list'][user]['Allowed'] and self.settings['Telegram']['White list'][user]['Subscribed']:
                res.append(user)
        return res
    def get_device_name(self, id):
        if id in self.settings['ZigBee']['Devices']:
            return self.settings['ZigBee']['Devices'][id]['name']
        else:
            return id

    def get_mqtt_ip(self):
        return self.settings['mqtt']['ip']
    def get_mqtt_port(self):
        return self.settings['mqtt']['port']

_config = Configuration()

def telegram_is_user_allowed(user: int):
    return _config.get_telegram_user_info(str(user))[0]

def telegram_is_user_subsribed(user: int):
    return _config.get_telegram_user_info(str(user))[1]

def telegram_set_user_subsribed(user: int, subscribed:bool):
    if _config.get_telegram_user_info(str(user))[0]:
        _config.set_telegram_user_info(str(user), subscribed)
        _config.write_settings()

def telegram_get_subsribed_users():
    return [int(x) for x in _config.get_telegram_subscribed_users()]


def devices_get_last_messages(short=True):
    result = ""
    for d in mqtt_control.get_devices_list():
        msg = mqtt_statistic.statisctic_get_last_record(d)
        name = _config.get_device_name(d)
        if msg != None:
            print(msg[1])
            if short:
                msg_formated = devices_callbacks[d]["Format short"](d, msg[1])
            else:
                msg_formated = "\n{}:\n{}".format(
                    msg[0],
                    devices_callbacks[d]["Format detailed"](d, msg[1]))
            result = result + name + ': ' + msg_formated + '\n'
        else:
            result = result + name + ': No  records\n'
    return result

def motion_detector_format_short(dev, payload):
    if payload['occupancy'] == True:
         return "motion was detected"
    else:
         return "motion wasn't detected"

def motion_detector_format_long(dev, payload):
    return json.dumps(payload, sort_keys=True, indent=4)

def temperature_format_short(dev, payload):
    return "Temperature {}\N{DEGREE SIGN}C humidity {}%".format(payload['temperature'],
                                                                payload['humidity'])

def temperature_format_long(dev, payload):
    return json.dumps(payload, sort_keys=True, indent=4)


def motion_detector_handler(dev, payload):
    if payload['occupancy'] == True:
        name = _config.get_device_name(dev)
        msg = devices_callbacks[dev]["Format short"](dev, payload)
        telegram_bot.send_message(_telegram_bot, name + ": " + msg)

prev_sent_message = {}
def temperature_handler(dev, payload):
    if not dev in  prev_sent_message:
        prev_message = None
    else:
        prev_message = prev_sent_message[dev]

    if prev_message == None or  abs(prev_message['temperature'] - payload['temperature']) > 1 or abs(prev_message['humidity'] - payload['humidity']) > 3:
       name = _config.get_device_name(dev)
       msg = devices_callbacks[dev]["Format short"](dev, payload)
       telegram_bot.send_message(_telegram_bot, name + ":" + msg)
       prev_sent_message[dev] = payload

devices_callbacks = {
     '0x00124b002916fe44': {
         "Format short": motion_detector_format_short,
         "Format detailed": motion_detector_format_long,
         "Handler": motion_detector_handler
     },
    '0xa4c138b9e8e9b978': {
        "Format short": temperature_format_short,
        "Format detailed": temperature_format_long,
         "Handler": temperature_handler,
    }
}

def mqtt_device_message(devices_tree):
    telegram_bot.send_html_message(_telegram_bot, dict_to_html(devices_tree))
    #print(devices_tree)

def dict_to_html(data, level=0):
    """Convert a nested dictionary into an HTML unordered list."""
    html = []
    indent = "  " * level

    for key, value in data.items():
        html.append(f"{indent}<strong>{key}:</strong>")
        if isinstance(value, dict):  # Recursive case for nested dictionaries
            html.append(dict_to_html(value, level+1))
        else:  # Base case for key-value pairs
            if key == 'friendly_name':
                html.append("{} - {}".format(indent, _config.get_device_name(value)))
            else:
                html.append(f"{indent} - {value}")
    return "\n".join(html)

def mqtt_message(device, msg):
    if device in devices_callbacks:
        devices_callbacks[device]["Handler"](device, msg)
    else:
        telegram_bot.send_message(_telegram_bot, msg)
    mqtt_statistic.statistic_append(device, msg)

def controller_init():
    _mqtt_context = mqtt_control.mqtt_init(_config.get_mqtt_ip(), _config.get_mqtt_port(), mqtt_message, mqtt_device_message)
    global _telegram_bot
    _telegram_bot = telegram_bot.telegram_bot_init(_config.get_telegram_token(), _mqtt_context)
    mqtt_statistic.statistic_init()
    mqtt_control.mqtt_run(_mqtt_context)


if __name__ == '__main__':
    controller_init()
