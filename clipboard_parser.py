# -*- coding: utf-8 -*-

import pyperclip
import io
import win32clipboard
from pynput.keyboard import Listener


def add_to_clipboard(text):
    pyperclip.copy(text)


def parse_data(copied_text):

    def text_refactoring(text):
        # removes keywords such "user" and "password" declinations from text
        def erase_keywords(text_to_clean):
            lines_to_clean = [line.strip() for line in text_to_clean]
            user_variances = ["usr:", "user:", "username:"]
            pwd_variances = ["pw:", "pwd:", "password:"]
            result = []
            for single_line in lines_to_clean:
                cleaned_line = single_line
                for entry in set(user_variances).union(set(pwd_variances)):
                    cleaned_line = cleaned_line.replace(entry, "")
                result.append(cleaned_line)
            return result

        return [line.strip() for line in erase_keywords(text)]

    # pick credentials from text
    def credentials_from_text(text):
        full_parameters_structure = "{hostname}\n{url}\n{username}\n{password}\n"
        partial_parameters_structure = "{hostname}\n{username}\n{password}\n"
        params = {}
        with io.StringIO(text) as reader:
            lines = text_refactoring(reader.readlines())

            if len(lines) is 3:
                params["hostname"] = lines[0]
                params["username"] = lines[1]
                params["password"] = lines[2]
                return partial_parameters_structure.format(**params)
            elif len(lines) is 4:
                params["hostname"] = lines[0]
                params["url"] = lines[1]
                params["username"] = lines[2]
                params["password"] = lines[3]
                return full_parameters_structure.format(**params)

            elif len(lines) is 1:
                words_in_line = lines[0].split(" ")

                if len(words_in_line) is 3:
                    params["hostname"] = words_in_line[0]
                    params["username"] = words_in_line[1]
                    params["password"] = words_in_line[2]
                    return partial_parameters_structure.format(**params)

                elif len(words_in_line) is 4:
                    params["hostname"] = words_in_line[0]
                    params["url"] = words_in_line[1]
                    params["username"] = words_in_line[2]
                    params["password"] = words_in_line[3]
                    return full_parameters_structure.format(**params)

    credentials = credentials_from_text(copied_text)
    print(credentials)
    add_to_clipboard(credentials)


def on_release(key):
    if str(key) == "'\\x11'":
        return False
    # if ctrl+d is pressed parse selection
    if str(key) == "'\\x03'":
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            print("Copied text: " + data)
            win32clipboard.CloseClipboard()
            parse_data(data.strip())

        except TypeError:
            print("Error")
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            return False
        except ...:
            print("Error")


# link to action
with Listener(on_release=on_release) as listener:
    print("Listening commands...")
    listener.join()
