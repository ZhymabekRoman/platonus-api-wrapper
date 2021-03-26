import json
from types import SimpleNamespace
from .exceptions import NotValidJSON

class json2object(object):
    """Класс который превращает JSON в объект
    Args:
        json_data: JSON который нужно перевести в объект
    """
    def __init__(self, json_data):
        self.__json_data = self.make_unicode(json_data)
        try:
            self.__json_object = json.loads(self.__json_data, object_hook=lambda d: SimpleNamespace(**d))
        except ValueError as e:
            raise NotValidJSON("Не валидный JSON")

    def make_unicode(self, input_str):
        if isinstance(input_str, str):
            return input_str
        else:
            return input_str.decode('utf-8')

    def __getattr__(self, name):
        return getattr(self.__json_object, name)

    def __len__(self):
        return len(json.loads(self.__json_data))

    def __repr__(self):
        return str(self.__json_data)
