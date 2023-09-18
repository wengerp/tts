# -*- coding: cp1252 -*-

import RPi_I2C_driver
import subprocess

mylcd = RPi_I2C_driver.lcd()

fontdata_uml = [
    [0b001010, 0b000000, 0b001110, 0b000001, 0b001111, 0b010001, 0b001111, 0b000000],
    [0b001010, 0b000000, 0b001110, 0b010001, 0b010001, 0b010001, 0b001110, 0b000000],
    [0b001010, 0b000000, 0b010001, 0b010001, 0b010001, 0b010011, 0b001101, 0b000000]
]


class Display:
    _version = "1.0.0"
    _author = "Patrick Wenger"

    def __init__(self, num_rows, num_cols, placeholder):
        self.__numRows = num_rows
        self.__numCols = num_cols
        self.__numBlocks = 6
        self.__placeholder = placeholder
        self.__numDigits = num_rows * num_cols
        self.__index = 0
        self.__charList = ""
        self.__posRow = 0
        self.__posCol = 0
        self.__posBlock = 0
        self.__language = "DE"
        self.__backlight = True
        self.init_display()
        self.__print_display()

    # -------------------------------------------------------------- getter and setter functions
    def __update_index(self, distance=1):
        if self.__index < self.__numDigits:
            self.__index += distance
            self.__posRow = self.__get_row_from_index()
            self.__posCol = self.__get_col_from_index()
        else:
            self.reset_position()

    # -------------------------------------------------------------- lifecycle methods
    def __str__(self):
        tmp = ''
        for k, v in self.__dict__.items():
            tmp += str(k) + " : " + str(v) + "\n"
        for row in range(0, self.__numRows):
            tmp += (self.__get_row_by_counter(row))
            tmp += "\n"
        return tmp

    def init_display(self):
        self.__charList = "                    "
        self.__charList += "                    "
        self.__charList += "                    "
        self.__charList += "                    "
        self.__charList += "                    "
        self.__charList += "                    "
        self.__charList += "                    "
        self.__charList += "                    "
        self.__charList += "                    "
        self.__charList += "                    "
        self.__charList += "                    "
        self.__charList += "                    "
        self.__index = 0
        mylcd.lcd_clear()
        mylcd.lcd_load_custom_chars(fontdata_uml)
        mylcd.lcd_display_string_pos(">", 1, 0)

    # TODO: something is wrong with the posBlock value. There is no error but
    #  one can only use 4 of the 6 blocks. Has to be analysed.
    def reset_position(self):
        self.__posRow = 0
        self.__posCol = 0
        self.__index = 0
        if self.__posBlock < self.__numBlocks:
            self.__posBlock += 1
        else:
            self.__posBlock = 0

    def clear_display(self):
        # self.reset_position()
        self.__posRow = 0
        self.__posCol = 0
        self.__posBlock = 0
        self.init_display()

    def __get_row_by_counter(self, counter):
        sout = ''
        sout += (self.__charList[(self.__numBlocks + 1) * counter * self.__numCols:
                                 (self.__numBlocks + 1) * counter * self.__numCols + self.__numCols])
        return sout

    def __print_display(self):
        for row in range(0, self.__numRows - 1):
            print(self.__get_row_by_counter(row))

    def set_backlight(self, on):
        mylcd.backlight(1) if on else mylcd.backlight(0)

    def set_language(self, lang):
        self.__language = lang

    # --------------------------------------------------------------process methods
    def ext_send_digit_to_display(self, digit):
        myrow = self.__get_row_from_index() + 1
        mycol = self.__get_col_from_index()
        mylcd.lcd_display_string_pos(digit, myrow, mycol)

    def modify_active_digit(self, digit):
        if self.__index < self.__numDigits:
            self.__charList = (self.__charList[:(self.__posBlock * self.__numDigits) + self.__index] + digit +
                               self.__charList[(self.__posBlock * self.__numDigits) + self.__index + 1:])
            self.__update_index()
            self.ext_send_digit_to_display(digit)
        else:
            self.reset_position()

    def modify_pre_active_digit(self):
        if self.__index >= 0:
            self.__index -= 1
            self.modify_active_digit(" ")
            self.__index -= 2
            self.modify_active_digit(self.__charList[(self.__posBlock * self.__numDigits) + self.__index])
        else:
            self.reset_position()

    def __get_row_from_index(self):
        return self.__index // self.__numCols

    def __get_col_from_index(self):
        return self.__index - (self.__get_row_from_index() * self.__numCols)

    def send_data_to_tts(self):
        text_to_say = self.__charList.strip()
        print('/home/wepa/Text2Speech/src/tts.sh "' + text_to_say + '" "' + self.__language + '"')
        the_command = ('/home/wepa/Text2Speech/src/tts.sh "' + text_to_say + '" "' + self.__language + '"')
        with subprocess.Popen(the_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            stdout = (proc.stdout.read())
            # stderr = (proc.stderr.read())
        stdout2 = stdout.decode('cp1252')
        print("stdout: %s" % stdout2)
        # print("stderr: %s" % stderr)

    @classmethod
    def get_version(cls):
        return cls._version

    @staticmethod
    def get_author():
        return Display._author
