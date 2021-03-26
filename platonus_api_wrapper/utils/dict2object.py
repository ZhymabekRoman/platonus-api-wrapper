
class dict2object:
    """Класс, который превращает словарь в объект
    Args:
        dictionary: словарь, который нужно перевести в объектё
    """
    def __init__(self, dictionary):
        self.__dict__.update(dictionary)

    def __repr__(self):
        return str(self.__dict__)
