#! /usr/bin/python
# -*- coding: cp1252 -*-

from pynput.keyboard import Key, Listener
from Display import *
from Watchdog import *
import os

hd44780 = Display(4, 20, " ")
print(hd44780)


class App:
    def show(key):
        if key == Key.backspace:
            hd44780.modify_pre_active_digit()
            return True
        elif key == Key.enter:
            hd44780.send_data_to_tts()
            hd44780.init_display()
            return True
        elif key == Key.space or key == Key.tab:
            simple_key = str(" ")
            hd44780.modify_active_digit(simple_key)
            return True
        elif key == Key.f1:
            hd44780.clear_display()
            return True
        elif key == Key.f2:
            return False
        elif key == Key.f4:
            os.system("sudo shutdown now")
            return False
        elif key == Key.f8:
            hd44780.set_language("FR")
            return True
        elif key == Key.f9:
            hd44780.set_language("EN")
            return True
        elif key == Key.f10:
            hd44780.set_language("DE")
            return True
        elif key == Key.shift or key == Key.ctrl:
            return True
        else:
            simple_key = str(key).replace("'", "")
            is_valid_key = simple_key >= 'a' and simple_key <= 'z'
            is_valid_key = is_valid_key or simple_key >= '0' and simple_key <= '9'
            is_valid_key = is_valid_key or simple_key >= 'ä' and simple_key <= 'ü'
            is_valid_key = is_valid_key or simple_key == "."
            is_valid_key = is_valid_key or simple_key == ","
            is_valid_key = is_valid_key or simple_key == "?"
            is_valid_key = is_valid_key or simple_key == "'"
            if is_valid_key:
                hd44780.modify_active_digit(simple_key)
            return True

    with Listener(on_press=show) as listener:
        listener.join()


def powersafe_display():
    print("switched off backlight")
    hd44780.set_backlight(False)
    Watchdog(180, powersafe_display)


Watchdog(180, powersafe_display)
