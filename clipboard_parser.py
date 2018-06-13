# -*- coding: utf-8 -*-

import pyperclip
import io
import win32clipboard
from pynput.keyboard import Listener


class Colors:
    GREEN = '\033[92m'


# constant values
FOUR_PARAMS_STRUCTURE = "{hostname}\n{url}\n{username}\n{password}\n"
THREE_PARAMS_STRUCTURE = "{hostname}\n{username}\n{password}\n"
USER_STRING_VARIANCES = ["usr:", "user:", "username:"]
PWD_STRING_VARIANCES = ["pw:", "pwd:", "password:"]


# add to clipboard text
def add_to_clipboard(text):
    pyperclip.copy(text)


def text_refactoring(text):
    # removes keywords such "user" and "password" declinations from text
    def erase_keywords(text_to_clean):
        lines_to_clean = [line.strip() for line in text_to_clean]
        result = []
        for single_line in lines_to_clean:
            cleaned_line = single_line
            for entry in set(USER_STRING_VARIANCES).union(set(PWD_STRING_VARIANCES)):
                cleaned_line = cleaned_line.replace(entry, "")
            result.append(cleaned_line)
        return result

    return [line.strip() for line in erase_keywords(text)]


# pick credentials from text
def credentials_from_text(text):

    params = {}
    with io.StringIO(text) as reader:
        lines = text_refactoring(reader.readlines())

        if len(lines) is 3:
            params["hostname"] = lines[0]
            params["username"] = lines[1]
            params["password"] = lines[2]
            return THREE_PARAMS_STRUCTURE.format(**params)

        elif len(lines) is 4:
            params["hostname"] = lines[0]
            params["url"] = lines[1]
            params["username"] = lines[2]
            params["password"] = lines[3]
            return FOUR_PARAMS_STRUCTURE.format(**params)

        elif len(lines) is 1:
            words_in_line = lines[0].split(" ")

            if len(words_in_line) is 3:
                params["hostname"] = words_in_line[0]
                params["username"] = words_in_line[1]
                params["password"] = words_in_line[2]
                return THREE_PARAMS_STRUCTURE.format(**params)

            elif len(words_in_line) is 4:
                params["hostname"] = words_in_line[0]
                params["url"] = words_in_line[1]
                params["username"] = words_in_line[2]
                params["password"] = words_in_line[3]
                return FOUR_PARAMS_STRUCTURE.format(**params)


# convert selected text into desired format
def parse_data(copied_text):
    credentials = credentials_from_text(copied_text)
    print(Colors.GREEN + "Copied text:\n{credentials}".format(credentials=credentials))
    add_to_clipboard(credentials)


# listener on keyboard action
def on_release(key):
    if str(key) == "'\\x11'":
        print("Script manually interrupted.")
        return False
    # if ctrl+d is pressed parse selection
    if str(key) == "'\\x04'":
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            parse_data(data.strip())

        except TypeError:
            print("Type error. Interrupting script.")
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            return False
        except pyperclip.PyperclipException:
            print("Impossible parsing selected text. Try again.")


# link to action
with Listener(on_release=on_release) as listener:
    print("Listening commands.\n"
          "Press CTRL+D to parse copied text\n"
          "Press CTRL+Q to kill the process.\n")
    listener.join()
