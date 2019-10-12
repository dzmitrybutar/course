import json
from collections import defaultdict
import xml.etree.cElementTree as et
import os
import argparse


class ValidationError(Exception):
    pass


class Loader:
    """Base class for loading data."""

    def __init__(self, path: str):
        self.path = path

    def load(self):
        raise NotImplementedError

    def check_existence(self):
        if not os.path.exists(self.path):
            raise ValidationError('{} not exist!'.format(self.path))

    def check_file_format(self, file_type):
        if not self.path.split('.')[-1] == file_type:
            raise ValidationError('Wrong file format!')


class JsonLoader(Loader):
    """Class for loading JSON data."""

    def load(self):
        self.check_existence()
        self.check_file_format('json')

        with open(self.path, 'r') as f:
            data = json.load(f)
            return data


class Converter:
    """Base class for data conversion."""

    def __init__(self, data: list):
        self.data = data

    def save(self):
        raise NotImplementedError


class JsonConverter(Converter):
    """Class for outputting data in JSON format."""

    def save(self):
        with open('data.json', 'w') as f:
            json.dump(self.data, f, sort_keys=True,
                      ensure_ascii=False, indent=4)


class XmlConverter(Converter):
    """Class for outputting data in XML format."""

    def save(self):
        rooms = et.Element("rooms")

        for s in self.data:
            room = et.SubElement(rooms, "room")
            id_room = et.SubElement(room, "id")
            name = et.SubElement(room, "name")
            students = et.SubElement(room, "students")
            id_room.text = str(s['id'])
            name.text = str(s['name'])
            students.text = str(s['students']).strip('[]')

        tree = et.ElementTree(rooms)
        tree.write("data.xml", xml_declaration=True)


class Action:
    """Class for working with input data."""
    def __init__(self, students: list, rooms: list):
        self.students = students
        self.rooms = rooms

    def union(self):
        """Combining data into a list of rooms where each room
        contains a list of students who are in this room.
        """

        d = defaultdict(list)

        for s in self.students:
            d[s['room']].append(s['id'])

        for r in self.rooms:
            for k in d:
                if r['id'] == k:
                    r['students'] = d[k]

        return self.rooms


def make(stud_path, rooms_path, mode):
    students = JsonLoader(stud_path).load()
    rooms = JsonLoader(rooms_path).load()
    data = Action(students, rooms).union()
    if mode == 'json':
        JsonConverter(data).save()
    if mode == 'xml':
        XmlConverter(data).save()


def main():
    """Run a script to process data."""
    parser = argparse.ArgumentParser(description='Merging rooms and students')
    parser.add_argument('student_dir', type=str, help='Students file path.')
    parser.add_argument('room_dir', type=str, help='Rooms file path')
    parser.add_argument('format', choices=['json', 'xml'], help='The output format.')
    args = parser.parse_args()
    basedir = os.path.abspath(os.path.dirname(__file__))
    stud_path = basedir + '/' + args.student_dir
    rooms_path = basedir + '/' + args.room_dir
    make(stud_path, rooms_path, args.format)


if __name__ == "__main__":
    main()
