import json
import os


def data_from_json(path):
    os.chdir(os.getcwd())
    with open(path, 'r') as f:
        data = json.load(f)
    return data