from collections import defaultdict


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
            r['students'] = d[r['id']]

        return self.rooms
