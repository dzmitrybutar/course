import json
import xml.etree.cElementTree as ET
import os
import argparse
from configparser import ConfigParser
from mysql.connector import MySQLConnection, Error


class ValidationError(Exception):
    pass


def read_db_config(filename='config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object"""

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
    """Class to connect to the database"""

    def __init__(self):
        db_config = read_db_config()
        self.connection = MySQLConnection(**db_config)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.cursor.close()
        self.connection.close()


class Database(Connection):
    """Class for working with database"""

    def insert(self, data: list, table: str):
        """Writing data to the database"""

        try:
            keys, values = zip(*data[0].items())
            list_arg = [tuple(d[k] for k in keys) for d in data]
            query = "INSERT IGNORE INTO {} ({}) values ({})".format(
                table, ",".join(keys), ",".join(['%s'] * len(keys)))
            self.cursor.executemany(query, list_arg)
            self.connection.commit()

        except Error as error:
            print("Failed to insert into MySQL table {}".format(error))

    def select(self, query: str):
        """Database query for data"""

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

    def __init__(self, data: list, out_name: str, format: str):
        self.data = data
        self.out_name = out_name
        self.format = format

    def get_name(self):
        if not os.path.exists('output_data'):
            os.makedirs('output_data')
        path = os.path.abspath('output_data')
        name = '{}/{}.{}'.format(path, self.out_name, self.format)
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


class ConverterFactory:
    """Factory class for defining output format"""

    def get_serializer(self, format: str, data: list, out_name: str):
        if format == 'json':
            return JsonConverter(data, out_name, format)
        elif format == 'xml':
            return XmlConverter(data, out_name, format)
        else:
            raise ValueError(format)


def make(stud_path: str, rooms_path: str, format: str):

    queries = dict(
        rooms_stud_count="SELECT rooms.name, COUNT(students.room) AS count_st "
                         "FROM rooms JOIN students ON rooms.id = students.room "
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

    converter = ConverterFactory()
    students = JsonLoader(stud_path).load()
    rooms = JsonLoader(rooms_path).load()
    database = Database()
    database.insert(rooms, 'rooms')
    database.insert(students, 'students')
    for k, v in queries.items():
        data = database.select(v)
        converter.get_serializer(format, data, k).save()


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
