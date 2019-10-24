import os
import json


class Loader:
    """Base class for loading data."""

    def __init__(self, path: str):
        self.path = path

    def load(self):
        raise NotImplementedError

    def check_existence(self):
        if not os.path.exists(self.path):
            raise FileExistsError('{} not exist!'.format(self.path))

    def check_file_format(self, file_type):
        if not self.path.split('.')[-1] == file_type:
            raise FileNotFoundError('Wrong file format!')


class JsonLoader(Loader):
    """Class for loading JSON data."""

    def load(self):
        self.check_existence()
        self.check_file_format('json')

        with open(self.path, 'r') as f:
            data = json.load(f)
            return data
