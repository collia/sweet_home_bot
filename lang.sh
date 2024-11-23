#!/bin/sh

xgettext -o telegram_bot.pot telegram_bot.py
msginit -l ua -o ua.po -i telegram_bot.pot

emacsclient ua.po

msgfmt ua.po -o ua/LC_MESSAGES/telegram_bot.mo
