import argparse
from configparser import ConfigParser
from loader import JsonLoader
from converter import ConverterFactory
from process_data import Process
from db_operations import MysqlExecutor


def read_db_config(config_path, section='database'):
    """ Read database configuration file and return a dictionary object."""

    parser = ConfigParser()
    parser.read(config_path)
    db = {}

    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise FileNotFoundError('{} not found in the {} file'.format(section, config_path))

    return db


def execute_queries(mode: str, db_config: dict):
    """Makes queries to the database and writes the received data in the required format."""

    queries = dict(
        rooms_stud_count="SELECT rooms.name, COUNT(students.room) AS count_st "
                         "FROM rooms LEFT JOIN students ON rooms.id = students.room "
                         "GROUP BY rooms.id",
        min_avg_old="SELECT rooms.name "
                    "FROM rooms JOIN students ON rooms.id = students.room "
                    "GROUP BY rooms.id "
                    "ORDER BY AVG(students.birthday) ASC "
                    "LIMIT 5",
        max_diff_old="SELECT rooms.name "
                     "FROM rooms JOIN students ON rooms.id = students.room "
                     "GROUP BY rooms.id "
                     "ORDER BY DATEDIFF(MAX(students.birthday), MIN(students.birthday)) DESC "
                     "LIMIT 5",
        room_two_sex="SELECT rooms.name "
                     "FROM rooms JOIN students ON rooms.id = students.room "
                     "GROUP BY rooms.id "
                     "HAVING COUNT(DISTINCT students.sex) > 1"
    )

    database = MysqlExecutor(db_config)
    converter = ConverterFactory(mode)
    for keys, values in queries.items():
        data = database.select(values)
        converter.get_serializer(data, keys).save()


def make(stud_path: str, rooms_path: str, config_path: str, mode: str):

    db_config = read_db_config(config_path)
    students = JsonLoader(stud_path).load()
    rooms = JsonLoader(rooms_path).load()
    stud_data, stud_fields = Process(rooms).process_for_insert()
    room_data, room_fields = Process(students).process_for_insert()
    database = MysqlExecutor(db_config)
    database.insert(stud_data, stud_fields, 'rooms')
    database.insert(room_data, room_fields, 'students')
    execute_queries(mode, db_config)


def main():
    """Run a script to process data."""

    parser = argparse.ArgumentParser(description='Merging rooms and students')
    parser.add_argument('student_dir', type=str, help='Students file path.')
    parser.add_argument('room_dir', type=str, help='Rooms file path')
    parser.add_argument('config_dir', type=str, help='Config file path')
    parser.add_argument('format', choices=['json', 'xml'], help='The output format.')
    args = parser.parse_args()
    make(args.student_dir, args.room_dir, args.config_dir, args.format)


if __name__ == "__main__":
    main()
