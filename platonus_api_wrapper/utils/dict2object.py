
class dict2object:
    def __init__(self, dictionary):
        self.__dictionary = dictionary
        self.__dict__.update(dictionary)

    def __repr__(self):
        return str(self.__dictionary)
