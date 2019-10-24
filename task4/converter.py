import json
import os
import xml.etree.cElementTree as ET


class Converter:
    """Base class for data conversion."""

    def __init__(self, data: list, out_name: str, mode: str):
        self.data = data
        self.out_name = out_name
        self.mode = mode

    def get_name(self):
        path = 'output_data_' + self.mode
        if not os.path.exists(path):
            os.makedirs(path)
        out_path = os.path.abspath(path)
        name = '{}/{}.{}'.format(out_path, self.out_name, self.mode)
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
