import json


class Datareader(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def get_data(self):
        with open(self.filepath, 'r') as f:
            data = json.load(f)
        return data
