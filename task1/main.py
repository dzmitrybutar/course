import argparse
from converter import ConverterFactory
from loader import JsonLoader
from process_data import Action


def make(stud_path: str, rooms_path: str, mode: str):
    converter = ConverterFactory(mode)
    students = JsonLoader(stud_path).load()
    rooms = JsonLoader(rooms_path).load()
    data = Action(students, rooms).union()
    converter.get_serializer(data).save()


def main():
    """Run a script to process data."""

    parser = argparse.ArgumentParser(description='Merging rooms and students')
    parser.add_argument('student_dir', type=str, help='Students file path.')
    parser.add_argument('room_dir', type=str, help='Rooms file path')
    parser.add_argument('format', choices=['json', 'xml'], help='The output format.')
    args = parser.parse_args()
    make(args.student_dir, args.room_dir, args.format)


if __name__ == "__main__":
    main()
