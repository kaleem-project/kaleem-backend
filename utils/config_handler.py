import json
import os

def read_json(filename):
    with open(filename, "r") as config_file:
        config = json.load(config_file)
    return config