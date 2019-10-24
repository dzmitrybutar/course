class Process:
    """Class for processing raw data."""

    def __init__(self, raw_data: list):
        self.raw_data = raw_data

    def process_for_insert(self):
        """Returns a list of fields and a list of records in a tuple."""

        fields = list(self.raw_data[0].keys())
        data = [tuple(d[f] for f in fields) for d in self.raw_data]

        return data, fields
