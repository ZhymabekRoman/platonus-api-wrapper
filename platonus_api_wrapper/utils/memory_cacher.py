from typing import Callable


class MemoryCacherMixin:
    def __init__(self):
        self.__memory_cacher: list[Callable] = []

    @property
    def _cached_functions_list(self) -> list[Callable]:
        return self.__memory_cacher

    @_cached_functions_list.setter
    def _cached_functions_list(self, value: Callable):
        for list_value in self.__memory_cacher:
            if list_value == value:
                return

        self.__memory_cacher.append(value)

    @_cached_functions_list.deleter
    def _cached_functions_list(self):
        for func in self.__memory_cacher:
            func.cache_clear()

        self.__memory_cacher = []
