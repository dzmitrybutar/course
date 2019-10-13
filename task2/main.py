import re
import functools


@functools.total_ordering
class Version:
    def __init__(self, version):
        self.__call__(version)

    expression = re.compile(
        r'^(\d+)\.(\d+)(\.(\d+))?[-.]?([a-z]+)?(\d+)?[-.]?([a-z]+)?(\d+)?$')

    def __call__(self, version):
        result = self.expression.match(version)

        if not result:
            raise ValueError("Invalid version '%s'" % version)

        self.num_list = list(result.group(1, 2, 4))
        if not result.group(4):
            self.num_list[2] = '0'
        self.num_list = list(map(int, self.num_list))

        self.pre_list = list(result.group(5, 6, 7, 8))
        if not self.pre_list == [None] * len(self.pre_list):
            for i, obj in enumerate(self.pre_list):
                try:
                    self.pre_list[i] = int(obj)
                except TypeError:
                    del self.pre_list[i]
                except ValueError:
                    pass
        else:
            self.pre_list = None

    def __eq__(self, other):
        a = self.cmp(other)
        if a is NotImplemented:
            return a
        return a == 0

    def __lt__(self, other):
        a = self.cmp(other)
        if a is NotImplemented:
            return a
        return a < 0

    def cmp(self, other):
        if isinstance(other, str):
            other = Version(other)
        if self.num_list != other.num_list:
            if self.num_list < other.num_list:
                return -1
            else:
                return 1
        if not self.pre_list and not other.pre_list:
            return 0
        elif self.pre_list and not other.pre_list:
            return -1
        elif not self.pre_list and other.pre_list:
            return 1
        elif self.pre_list and other.pre_list:
            if self.pre_list == other.pre_list:
                return 0
            elif self.pre_list < other.pre_list:
                return -1
            else:
                return 1


def main():
    to_test = [
        ('1.0.0', '2.0.0'),
        ('1.0.0', '1.42.0'),
        ('1.2.0', '1.2.42'),
        ('1.1.0-alpha', '1.1.0-beta'),
        ('1.0.1b', '1.0.10-alpha.beta'),
        ('1.0.0-rc.1', '1.0.0'),
        ('1.22.3b1', '1.22.3-rc1.2')
    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), 'le failed'
        assert Version(version_2) > Version(version_1), 'ge failed'
        assert Version(version_2) != Version(version_1), 'neq failed'


if __name__ == "__main__":
    main()
