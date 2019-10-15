import functools


@functools.total_ordering
class Version:
    def __init__(self, version):
        self.__parse(version)

    def __parse(self, version):
        vstring = version.replace('-', '.')
        if not vstring.replace('.', '').isdigit():
            for i, c in enumerate(vstring):
                if c.isalpha():
                    self.num_list = self.__str_digits_to_int(
                        vstring[:i].strip('.').split('.'))
                    self.pre_list = self.__str_digits_to_int(
                        vstring[i:].strip('.').split('.'))
                    break
        else:
            self.num_list = self.__str_digits_to_int(vstring.split('.'))
            self.pre_list = None

        if len(self.num_list) == 2:
            self.num_list += [0]

    @staticmethod
    def __str_digits_to_int(vlist):
        for i in range(len(vlist)):
            if vlist[i].isdigit():
                vlist[i] = int(vlist[i])
        return vlist

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
        ('1.22.3b.1', '1.22.3-rc.1'),
        ('1.1.23b', '1.2'),
        ('1.2.0alpha', '1.2'),
        ('1.1.1alpha', '1.1.1-alpha1')
    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), 'le failed'
        assert Version(version_2) > Version(version_1), 'ge failed'
        assert Version(version_2) != Version(version_1), 'neq failed'


if __name__ == "__main__":
    main()