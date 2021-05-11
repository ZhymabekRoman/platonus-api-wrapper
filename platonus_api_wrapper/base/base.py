#! /usr/bin/env python3
# encoding: utf-8

from . import api
from ..utils import exceptions
from ..utils.dict2object import dict2object
from ..utils.base64 import base64_encode, base64_decode

from .profile import Profile
from .has_module import HasModule

from ..utils.request import RequestSessionWrapper
from ..utils.payload import generate_payload
from ..utils.lru_cacher import timed_lru_cache
from ..utils.loginizer import login_required

from ..validators import ValidateLoginCredentials
from ..validators import URLValidator, URLNormalizer
from ..validators import ValidateLanguage, LanguageCodeToInt

import logging
import pickle


"""
Platonus_API_Wrapper
~~~~~~~~~~~~~~~~~~~
This library provides a very thin wrapper around the
Platonus REST API.
"""

logger = logging.getLogger('platonus_api_wrapper')


class PlatonusBase:
    """
    Base class for Platonus API.

    Args:
        base_url: URL адресс Платонуса
        language: язык = ru - Русскии
                         kz - Казахскии
                         en - English
        context_path: корневой контекст URL адреса, где находится Платонус, обычно это /. К примеру колледж может на сайт example.kz установить Wordpress
                    и вести там главную страницу колледжа, а Платонус поставить на example.kz/platonus, вот как раз /platonus является контекстом Платонуса.
                    Более подробнее читайте здесь: https://medium.com/javascript-essentials/what-is-context-path-d442b3de164b
        auto_relogin_after_session_expires: автоматическая реавторизация после истекании срока сессии
    """
    def __init__(self, base_url: str, language: str = "ru", context_path: str = "/", auto_relogin_after_session_expires=True):
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

        # Инициализируем хранилище закэшированных функции. Это нужно для того чтобы во время выхода из аккаунта (или сесии, logout короче) очистить все закэшированные значения, мало ли.
        self.__memory_cacher = []

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
    def _cached_functions_list(self):
        return self.__memory_cacher

    @_cached_functions_list.setter
    def _cached_functions_list(self, value):
        for list_value in self.__memory_cacher:
            if list_value == value:
                return
        self.__memory_cacher.append(value)

    @_cached_functions_list.deleter
    def _cached_functions_list(self):
        for func in self.__memory_cacher:
            func.cache_clear()
        self.__memory_cacher = []

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
        try:
            if self.session:
                del self.session
        except AttributeError:
            logger.warning("Object session is not initialized, ignoring ...")


class PlatonusAPI(PlatonusBase):
    """
    Base Platonus API class

    Главный класс для работы с Платонусом. Взаимодействие происходит на уровне REST API.
    Информации о REST API были получены путем обратной разработки веб приложении и Android клиента, так как в свободном доступе нету ни исходников Платонуса, ни документации (комерческая тайна).
    """
    def login(self, login: str = None, password: str = None, IIN: str = None):
        """
        Авторизация в Платонус
        Args:
            username: логин
            password: пароль
            IIN: ИИН
        Returns:
            message: В случае если во время авторизации возникнет ошибка (неверный логин/ИИН/пароль) тогда выдаст сообщение об ошибке
            login_status: success если авторизация успешна, invalid если были введены не верные авторизационные данные
            auth_token: авторизационный токен
            sid: не известно
            uid: не известно
            personID: ID пользывателя
            personType (personRoleTypes): Тип пользывателя - 1: Обучающиеся
                                                             3: Преподаватель
                                                             38: Родитель
        """
        payload = generate_payload(**locals())

        ValidateLoginCredentials(dict2object(payload), self._auth_type_value)

        response = self.session.post(self.api.login, payload).json(object_hook=dict2object)

        if response.login_status == "invalid":
            raise exceptions.NotCorrectLoginCredentials(response.message)

        self.session.request_header = {'token': response.auth_token}
        self._auth_credentials = payload

        return response

    def login_with_eds(self):
        """Авторизация в Платонус при помощи ЭЦП

        Функция не реализована, т.к. у нас в колледже выключена возможность авторизации по ЭЦП, соответственно я не могу реализовать то, к чему я не имею доступ

        Информация для разработчиков, возможно кто-то сможет реализовать:
            url: 'rest/api/login/eds'
            type: 'GET'
        """
        raise NotImplementedError("Функция не реализованa")

    @login_required
    def logout(self):
        response = self.session.post(self.api.logout)

        # Очищаем хранилище авторизационных данных, тем самым указывая что пользыватель не авторизован
        self._auth_credentials = {}
        # И заодно токен тоже удаляем из хейдера запросов
        self.session.request_header = {'token': None}
        # Очищаем хранилище кэша от закэшированных запросов
        del self._cached_functions_list

        # После отправки запроса на выход из сессии сервер Платонуса ничего не отправляет кроме статус кода
        if response.status_code == 204:
            return dict2object({"logout_status": "success"})
        else:
            return dict2object({"logout_status": "unknown"})

    @login_required
    def change_login_or_password(self, old_password, new_password, confirm_new_password, new_login=None):
        if not new_login:
            new_login = self._auth_credentials["login"]

        if new_password != confirm_new_password:
            raise exceptions.NotCorrectLoginCredentials("Новый пароль и его подтверждение не совпадают")
        elif old_password != self._auth_credentials["password"]:
            raise exceptions.NotCorrectLoginCredentials("Вы ввели не верный старый пароль")
        elif old_password == new_password:
            raise exceptions.NotCorrectLoginCredentials("Новый и старый пароль одинаковы, смысл тогда менять пароль ?!")
        elif len(new_login) < 4 or len(new_password) < 4:
            raise exceptions.NotCorrectLoginCredentials("Длина логина/пароля должна быть не менее 4 символов")

        payload = {"login": new_login, "oldPassword": old_password, "password": new_password, "confPassword": confirm_new_password}
        response = self.session.post("rest/api/changePassword", payload).json(object_hook=dict2object)

        self._auth_credentials["login"] = new_login
        self._auth_credentials["password"] = new_password

        return response

    @timed_lru_cache(86400)
    def person_type_list(self):
        """По идее должен возврящать список типов пользывателей Platonus, но почему-то ничего не возвращяет, нафиг его тогда  реализовали?!"""
        response = self.session.get(self.api.person_type_list).json(object_hook=dict2object)
        return response

    @login_required
    @timed_lru_cache(60)
    def student_tasks(self, countInPart, endDate, partNumber, recipientStatus, startDate, studyGroupID="-1", subjectID="-1", term="-1", topic="", tutorID="-1", year="-1"):
        """Возвращает все задания ученика"""
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
    @timed_lru_cache(43200)
    def terms_list(self):
        """Возвращает список семестров"""
        response = self.session.get(self.api.terms_list).json(object_hook=dict2object)
        return response

    @login_required
    @timed_lru_cache(43200)
    def student_journal(self, year: int, term: int):
        """
        Возвращает журнал ученика
        Принимаемые аргументы: (см. также функцию study_years_list())
            year - год
            term - семестр
        """
        response = self.session.get(self.api.student_journal(year, term)).json(object_hook=dict2object)
        return response

    @login_required
    @timed_lru_cache(86400)
    def recipient_statuses_list(self):
        """Возвращает список всех возможных статусов задании"""
        response = self.session.get(self.api.recipient_statuses_list).json(object_hook=dict2object)
        return response

    def platonus_icon(self, icon_size: str = "small"):
        """
        Возвращает иконку Плаонуса в формате PNG
        Args:
            icon_size = принимает размер иконки: small или big
        """
        response = self.session.get(f'img/platonus-logo-{icon_size}.png', stream=True)
        return response.content

    def emblem_image(self):
        """Возвращает эмблему колледжа/университета в формате JPG"""
        response = self.session.get("images/emblem.jpg", stream=True)
        return response.content

    @timed_lru_cache(30)
    def server_time(self):
        """
        Возвращает текущее серверное время Плаонуса
        Returns:
            hour: час
            minute: минута
            date: дата
            dayOfWeek: день недели
        """
        response = self.session.get(self.api.server_time).json(object_hook=dict2object)
        return response

    @timed_lru_cache(600)
    def rest_api_information(self):
        """
        Возвращает данные об Платонусе
        Returns:
            productName: название продукта
            VERSION: версия Платонуса
            BUILD_NUMBER: версия билда Платонуса
            year: текущии год
            developerLink: ссылка на сайт разработчиков Платонуса
            developerName: разработчики
            licenceType (appType): тип лицензии / для кого предназначен - college: колледж
                                                                          university: университет
        """
        response = self.session.get('rest/api/version').json(object_hook=dict2object)
        return response

    @timed_lru_cache(3600)
    def auth_type(self):
        """
        Возвращает тип авторизации в Платонус
        Returns:
            value:  1 - логин и пароль
                    2 - ИИН, логин и пароль
                    3 - ИИН и пароль
                    4 - ничего (?)
        """
        response = self.session.get(self.api.auth_type).json(object_hook=dict2object)
        return response

    @timed_lru_cache(3600)
    def has_unshown_release(self):
        response = self.session.get(self.api.has_unshown_release).json(object_hook=dict2object)
        return response

    @login_required
    @timed_lru_cache(60)
    def survey_notifications(self):
        response = self.session.get(self.api.survey_notifications).json(object_hook=dict2object)
        return response

    @login_required
    @timed_lru_cache(60)
    def notifications(self):
        response = self.session.get(self.api.notifications).json(object_hook=dict2object)
        return response

    @property
    def profile(self):
        return Profile(self)

    @property
    def has_module(self):
        return HasModule(self)
