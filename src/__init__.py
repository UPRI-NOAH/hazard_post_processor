"""
Please use this only in settings.py
helper functions for getting env var
"""
import os
from distutils.util import strtobool


def get_str(var_name, default=None):

    return os.getenv(var_name) or default


def get_bool(var_name, default=None):

    value = os.getenv(var_name) or default

    return bool(strtobool(value))


def get_list(var_name, default=None):
    value = os.getenv(var_name)

    return value.split(",") if value else default


def get_int(var_name, default):
    try:
        value = os.getenv(var_name)

        return int(value) if value else default
    except ValueError:
        raise Exception(f"{var_name} not an int value")
