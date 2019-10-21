import json
import xml.etree.cElementTree as ET
import os
import argparse
from configparser import ConfigParser
from mysql.connector import MySQLConnection, Error


def read_db_config(filename='config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object."""

    parser = ConfigParser()
    parser.read(filename)
    db = {}

    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Error('{0} not found in the {1} file'.format(section, filename))

    return db


class Connection:
    """Class to connect to the database."""

    def __init__(self):
        db_config = read_db_config()
        self.connection = MySQLConnection(**db_config)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.cursor.close()
        self.connection.close()


class Database(Connection):
    """Class for working with the database."""

    def insert(self, data: list, fields: list, table: str):
        """Writing data to the database"""

        try:
            query = "INSERT IGNORE INTO {} ({}) values ({})".format(
                table, ",".join(fields), ",".join(['%s'] * len(fields)))
            self.cursor.executemany(query, data)
            self.connection.commit()

        except Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def select(self, query: str):
        """Database query for data."""

        try:
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            return records

        except Error as error:
            print("Failed to select into MySQL table {}".format(error))


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


class Converter:
    """Base class for data conversion."""

    def __init__(self, data: list, out_name: str, mode: str):
        self.data = data
        self.out_name = out_name
        self.mode = mode

    def get_name(self):
        if not os.path.exists('output_data'):
            os.makedirs('output_data')
        path = os.path.abspath('output_data')
        name = '{}/{}.{}'.format(path, self.out_name, self.mode)
        return name

    def save(self):
        raise NotImplementedError


class JsonConverter(Converter):
    """Class for outputting data in JSON format."""

    def save(self):
        output_dir = self.get_name()

        with open(output_dir, 'w') as f:
            json.dump(self.data, f, sort_keys=True,
                      ensure_ascii=False, indent=4)


class XmlConverter(Converter):
    """Class for outputting data in XML format."""

    def save(self):
        output_dir = self.get_name()
        result = ET.Element("result")

        for raw_d in self.data:
            d = list(raw_d)
            a = ET.SubElement(result, "a")
            a.text = str(d).strip('[]')

        tree = ET.ElementTree(result)
        tree.write(output_dir, xml_declaration=True)


class Process:
    """Class for processing raw data."""

    def __init__(self, raw_data: list):
        self.raw_data = raw_data

    def process_for_insert(self):
        """Returns a list of fields and a list of records in a tuple."""

        fields = list(self.raw_data[0].keys())
        data = [tuple(d[f] for f in fields) for d in self.raw_data]

        return data, fields


class ConverterFactory:
    """Factory class for defining output format."""

    def __init__(self, mode: str):
        self.mode = mode

    def get_serializer(self, data: list, out_name: str):
        if self.mode == 'json':
            return JsonConverter(data, out_name, self.mode)
        elif self.mode == 'xml':
            return XmlConverter(data, out_name, self.mode)
        else:
            raise ValueError(self.mode)


def execute_queries(mode: str):
    """Makes queries to the database and writes the received data in the required format."""

    queries = dict(
        rooms_stud_count="SELECT rooms.name, COUNT(students.room) AS count_st "
                         "FROM rooms LEFT JOIN students ON rooms.id = students.room "
                         "GROUP BY rooms.id",
        max_avg_old="SELECT rooms.name "
                    "FROM rooms JOIN students ON rooms.id = students.room "
                    "GROUP BY rooms.id "
                    "ORDER BY AVG(students.birthday) DESC "
                    "LIMIT 5",
        max_diff_old="SELECT rooms.name "
                     "FROM rooms JOIN students ON rooms.id = students.room "
                     "GROUP BY rooms.id "
                     "ORDER BY DATEDIFF(MAX(students.birthday), MIN(students.birthday)) DESC "
                     "LIMIT 5",
        room_two_sex="SELECT rooms.name "
                     "FROM rooms JOIN students ON rooms.id = students.room "
                     "GROUP BY rooms.id "
                     "HAVING COUNT(DISTINCT students.sex) in (2)"
    )

    database = Database()
    converter = ConverterFactory(mode)
    for keys, values in queries.items():
        data = database.select(values)
        converter.get_serializer(data, keys).save()


def make(stud_path: str, rooms_path: str, mode: str):

    students = JsonLoader(stud_path).load()
    rooms = JsonLoader(rooms_path).load()
    stud_data, stud_fields = Process(rooms).process_for_insert()
    room_data, room_fields = Process(students).process_for_insert()
    database = Database()
    database.insert(stud_data, stud_fields, 'rooms')
    database.insert(room_data, room_fields, 'students')
    execute_queries(mode)


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
