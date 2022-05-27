import re

SPECIAL_CHARACTERS = "!#$%^&*()-?_=,<>/|"


def has_special_char(string):
  return any(c in SPECIAL_CHARACTERS for c in string)


def has_int(string):
    return any(char.isdigit() for char in string)


def remove_int(string):
    return re.sub(r"\d+", "", string)


def is_num(string):
    try:
        float(string.strip().replace(",", ""))
        return True
    except:
        return False