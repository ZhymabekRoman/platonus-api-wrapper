#! /usr/bin/env python3
# encoding: utf-8

from . import api
from ..utils import exceptions
from ..utils.dict2object import dict2object
from ..utils.base64 import base64_encode, base64_decode

from ..utils.request import RequestSessionWrapper
from ..utils.payload import generate_payload

from ..validators import ValidateLoginCredentials
from ..validators import URLValidator, URLNormalizer
from ..validators import ValidateLanguage, LanguageCodeToInt

import pickle
import functools

"""
Platonus_API_Wrapper
~~~~~~~~~~~~~~~~~~~
This library provides a very thin wrapper around the
Platonus REST API.
"""


def login_required(method):
    """Make sure user is logged in before proceeding"""
    @functools.wraps(method)
    def wrapper_login_required(self, *args, **kwargs):

        if not self.user_is_authed:
            raise exceptions.NotCorrectLoginCredentials("Вы не авторизовались в Платонус. Пожалуйста выполните метод login, и укажите авторизационные данные")

        if not self.auto_relogin_after_session_expires:
            return method(self, *args, **kwargs)

        try:
            return method(self, *args, **kwargs)
        except exceptions.LoginSessionExpired:
            print("Login session is expired, reloging...")
            self.login(**self._auth_credentials)
            return method(self, *args, **kwargs)
    return wrapper_login_required


class PlatonusBase:
    """
    Base class for Platonus API.

    Принимаемые аргументы:
        base_url - URL адресс Платонуса
        language - язык = ru - Русскии
                          kz - Казахскии
                          en - English
        context_path - корневой контекст URL адреса, где находится Платонус, обычно это /. К примеру колледж может на сайт example.kz установить Wordpress
                    и вести там главную страницу колледжа, а Платонус поставить на example.kz/platonus, вот как раз /platonus является контекстом Платонуса.
                    Более подробнее читайте здесь: https://medium.com/javascript-essentials/what-is-context-path-d442b3de164b
        check_api_compatibility - проверка на совместимость данной библиотеки с Platonus сайтом.
        auto_relogin_after_session_expires - автоматическая реавторизация после истекании срока сессии
    """
    def __init__(self, base_url: str, language: str = "ru", context_path: str = "/", check_api_compatibility: bool = False, auto_relogin_after_session_expires=True):
        # Проверка URL адреса на валидность
        URLValidator(base_url)

        # Проверка выставленного языка на валидность
        ValidateLanguage(language)

        # Нормализуем адресс Платонуса. Для чего нужна нормализация URL адресса см. файл validators/URL.py
        platonus_url = URLNormalizer(base_url, context_path)

        # Инициализируем сессию
        self.session = RequestSessionWrapper(platonus_url)

        # Инициализируем язык Платонуса в хэйдер запросов
        self.session.request_header = {'language': LanguageCodeToInt(language)}

        # Инициализируем хранилище значении авторизационных данных, чтобы можно было автоматическии переавторизоватся в случае истекании сессиии
        self._auth_credentials = {}

        # Инициализируем менеджер REST API методов
        self.api = api.Methods(language, self.rest_api_version)

        # Инициализируем значение автоматиеского релогина после истекании сесии
        self.auto_relogin_after_session_expires = auto_relogin_after_session_expires

    def import_session(self, session_file):
        """
        Импортирует сессию Платонуса из файла. Это позваляет каждый раз не логинится,
        достаточно залогинится, экспортировать сессию через export_session и в нужый момент зайти в сессию через import_session.
        """
        with open(session_file, 'rb') as f:
            self.session.request_session, self._auth_credentials = pickle.load(f)

    def export_session(self, session_file):
        """
        Экспортирует сессию Платонуса в файл. Это позваляет каждый раз не логинится,
        достаточно залогинится, экспортировать сессию через export_session и в нужый момент зайти в сессию через import_session.
        """
        with open(session_file, 'wb') as f:
            pickle.dump((self.session.request_session, self._auth_credentials), f)

    @property
    def _auth_type_value(self):
        return self.auth_type().value

    @property
    def rest_api_version(self):
        rest_info = self.rest_api_information()
        return dict2object({"version": float(rest_info.VERSION), "build_number": int(rest_info.BUILD_NUMBER)})

    @property
    def user_is_authed(self):
        """Checks whether credentials were passed."""

        return True if self._auth_credentials else False

    def __del__(self):
        """
        When PlatonusAPI object is deleting - need close all sessions
        """
        if self.session:
            del self.session


class PlatonusAPI(PlatonusBase):
    """
    Base Platonus API class

    Главный класс для работы с Платонусом. Взаимодействие происходит на уровне REST API.
    Информации о REST API были получены путем обратной разработки веб приложении и Android клиента, так как в свободном доступе нету ни исходников Платонуса, ни документации (комерческая тайна).
    """
    def login(self, login: str = None, password: str = None, IIN: str = None):
        """
        Авторизация в Платонус
        Принимаемые аргументы:
            username - логин
            password - пароль
            IIN - ИИН
        """
        payload = generate_payload(**locals())

        ValidateLoginCredentials(dict2object(payload), self._auth_type_value)

        response = self.session.post(self.api.login, payload).json(object_hook=dict2object)

        if response.login_status == "invalid":
            raise exceptions.NotCorrectLoginCredentials(response.message)

        self.session.request_header = {'token': response.auth_token}
        self._auth_credentials = payload

        return response

    @login_required
    def logout(self):
        self._auth_credentials = {}

        response = self.session.post(self.api.logout)

        if response.status_code == 204:
            return dict2object({"logout_status": "success"})
        else:
            return dict2object({"logout_status": "unknown"})

    @login_required
    def profile_picture(self):
        """Возврашяет аватарку пользывателя"""
        response = self.session.get(self.api.profile_picture, stream=True).content
        return base64_decode(response)

    def person_type_list(self):
        """По идее должен возврящать список типов пользывателей Platonus, но плчему-то ничего не возвращяет, нафиг его тогда  реализовали?!"""
        response = self.session.get(self.api.person_type_list).json(object_hook=dict2object)
        return response

    @login_required
    def person_fio(self):
        """Возврашяет ФИО пользывателя"""
        response = self.session.get(self.api.person_fio)
        return response.text

    @login_required
    def person_info(self):
        """
        Возврашяет информацию о пользывателе
        Возвращаемые значения:
            lastName - Фамилия
            firstName - Имя
            patronymic - Отчество
            personType - Тип пользывателя = 1 - ученик
                                            0 - учитель (это не точно)
            photoBase64 - Фотография пользывателя в base64
            passwordExpired - Истек ли пароль пользывателя (bool значение)
            temporaryPassword - Стоит ли временный пароль (bool значение)
            studentID - ID ученика
            gpa - бог знает, скорее всего средяя оценка по всем урокам
            courseNumber - курс ученика
            groupName - название группы
            professionName - название специальности
            specializationName - название специализации
            studyTechnology - тип обучаемой технологии = 2 - по оценкам (5/4/3/2) (но это не точно)
        """
        response = self.session.get(self.api.person_info).json(object_hook=dict2object)
        return response

    @login_required
    def student_tasks(self, countInPart, endDate, partNumber, recipientStatus, startDate, studyGroupID="-1", subjectID="-1", term="-1", topic="", tutorID="-1", year="-1"):
        """Возвращяет все задания ученика"""
        payload = generate_payload(**locals())
        response = self.session.post(self.api.student_tasks, payload).json(object_hook=dict2object)
        return response

    @login_required
    def recipient_task_info(self, recipient_task_id):
        response = self.session.get(self.api.recipient_task_info(recipient_task_id)).json(object_hook=dict2object)
        return response

    @login_required
    def study_years_list(self):
        response = self.session.get(self.api.study_years_list).json(object_hook=dict2object)
        return response

    @login_required
    def get_marks_by_date(self):
        response = self.session.get(self.api.get_marks_by_date).json(object_hook=dict2object)
        return response

    @login_required
    def terms_list(self):
        """Возвращяет список семестров"""
        response = self.session.get(self.api.terms_list).json(object_hook=dict2object)
        return response

    @login_required
    def student_journal(self, year: int, term: int):
        """
        Возвращяет журнал ученика
        Принимаемые аргументы: (см. также функцию study_years_list())
            year - год
            term - семестр
        """
        response = self.session.get(self.api.student_journal(year, term)).json(object_hook=dict2object)
        return response

    @login_required
    def recipient_statuses_list(self):
        """Возвращяет список всех возможных статусов задании"""
        response = self.session.get(self.api.recipient_statuses_list).json(object_hook=dict2object)
        return response

    def platonus_icon(self, icon_size: str = "small"):
        """
        Возврашяет иконку Плаонуса в формате PNG
        Принимаемые аргументы:
            icon_size = принимает размер иконки: small или big
        """
        response = self.session.get(f'img/platonus-logo-{icon_size}.png', stream=True)
        return response.content

    def server_time(self):
        """
        Возвращает текущее серверное время Плаонуса
        ВНИМАНИЕ: АДРЕС REST API МЕНЯЕТСЯ В РАЗНЫХ ВЕРСИЯХ ПЛАТОНУСА!
        Возвращяемые значения:
            hour - час
            minute - минута
            date - дата
            dayOfWeek - день недели
        """
        response = self.session.get(self.api.server_time).json(object_hook=dict2object)
        return response

    def rest_api_information(self):
        """
        Возвращает данные об Платонусе
        Возвращаемые значения:
            productName - название продукта
            VERSION - версия Платонуса
            BUILD_NUMBER - версия билда Платонуса
            year - текущии код
            developerLink - ссылка на сайт разработчиков Платонуса
            developerName - разработчики
            licenceType - тип лицензии = college - колледж
                                         university - университет
        """
        response = self.session.get('rest/api/version').json(object_hook=dict2object)
        return response

    def auth_type(self):
        """
        Возвращает тип авторизации в Платонус
        Возвращаемые значения:
            value = 1 - логин и пароль
                    2 - ИИН, логин и пароль
                    3 - ИИН и пароль
                    4 - ничего (?)
        """
        response = self.session.get(self.api.auth_type).json(object_hook=dict2object)
        return response
