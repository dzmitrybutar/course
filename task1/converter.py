import os
import json
import xml.etree.cElementTree as et


class Converter:
    """Base class for data conversion."""

    def __init__(self, data: list, mode: str):
        self.data = data
        self.mode = mode

    def save(self):
        raise NotImplementedError

    def get_name(self):
        path = 'output_data_' + self.mode
        if not os.path.exists(path):
            os.makedirs(path)
        out_path = os.path.abspath(path)
        name = '{}/{}.{}'.format(out_path, 'data', self.mode)
        return name


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
        tree.write(output_dir, xml_declaration=True)


class ConverterFactory:
    """Factory class for defining output format"""

    def __init__(self, mode: str):
        self.mode = mode

    def get_serializer(self, data: list):
        if self.mode == 'json':
            return JsonConverter(data, self.mode)
        elif self.mode == 'xml':
            return XmlConverter(data, self.mode)
        else:
            raise ValueError(self.mode)
