#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mqtt_control
import telegram_bot
import json

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


def send_message(msg):
    telegram_bot.send_message(_telegram_bot, msg)


def controller_init():
    _mqtt_context = mqtt_control.mqtt_init(send_message)
    global _telegram_bot
    _telegram_bot = telegram_bot.telegram_bot_init(_config.get_telegram_token(), _mqtt_context)
    mqtt_control.mqtt_run(_mqtt_context)


if __name__ == '__main__':
    controller_init()
