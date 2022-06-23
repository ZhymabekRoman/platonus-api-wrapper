from ..utils.base64 import base64_decode
from ..utils.loginizer import login_required
from ..utils.lru_cacher import timed_lru_cache
from ..utils.dict2object import dict2object
from ..utils.base_cls_inject import inheritance_from_base_cls


class Profile(object):
    def __init__(self, base_cls):
        self.base_cls = base_cls

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def person_fio(self):
        """Возвращает ФИО пользывателя"""
        response = self.session.get(self.api.person_fio)
        return response.text

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(86400)
    def person_id(self):
        """Возвращает ID пользывателя"""
        response = self.session.get(self.api.person_id).as_object()
        return response

    @inheritance_from_base_cls
    @login_required
    def profile_picture(self):
        """Возвращает аватарку пользывателя"""
        response = self.session.get(self.api.profile_picture).content
        return base64_decode(response)

    @inheritance_from_base_cls
    @login_required
    @timed_lru_cache(3600)
    def profile_info(self):
        """
        Возвращает информацию о текущем пользывателе
        Returns:
            lastName: Фамилия
            firstName: Имя
            patronymic: Отчество
            personType: Тип пользывателя - 1: Обучающиеся
                                           3: Преподаватель
                                           38: Родитель
            photoBase64: Фотография пользывателя в base64
            passwordExpired: Истек ли пароль пользывателя (bool значение)
            temporaryPassword: Стоит ли временный пароль (bool значение)
            studentID: ID обучающегося
            gpa: бог знает, скорее всего средняя оценка по всем урокам
            courseNumber: курс ученика
            groupName: название группы (потока)
            professionName: название специальности
            specializationName: название специализации
            studyTechnology: тип обучаемой технологии = 2 - по оценкам (5/4/3/2) (но это не точно)
        """
        response = self.session.get(self.api.profile_info).as_object()
        return response
