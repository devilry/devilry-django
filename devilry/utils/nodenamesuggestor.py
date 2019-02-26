import re


class Suggest(object):
    """
    Suggests short and long name by adding 1 to any common
    number suggfixed in the given short and long name.
    """
    pattern = re.compile(r'^.+?(?P<suffixnumber>\d+)$')

    def __init__(self, long_name, short_name):
        self.long_name = long_name
        self.short_name = short_name
        self.number = self.__find_common_number()
        self.suggested_short_name = ''
        self.suggested_long_name = ''
        if self.number is not None:
            self.__suggest_names_from_number()

    def has_suggestion(self):
        return self.number is not None

    def __extract_number(self, name):
        match = self.pattern.match(name)
        if match:
            return int(match.group(1))
        else:
            return None

    def __find_common_number(self):
        """
        If both short and long name is suffixed with the same number,
        return the number as an int. If not, return ``None``.
        """
        short_name_number = self.__extract_number(self.short_name)
        if short_name_number is None:
            return None
        long_name_number = self.__extract_number(self.long_name)
        if long_name_number is None:
            return None
        if short_name_number == long_name_number:
            return short_name_number
        else:
            return None

    def __suggest_name_from_number(self, name):
        match = self.pattern.match(name)
        prefix = name[:match.start(1)]
        suggested_name = '{}{}'.format(prefix, self.number + 1)
        return suggested_name

    def __suggest_names_from_number(self):
        self.suggested_long_name = self.__suggest_name_from_number(self.long_name)
        self.suggested_short_name = self.__suggest_name_from_number(self.short_name)
