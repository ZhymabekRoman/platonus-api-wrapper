#! /usr/bin/env python
# encoding: utf-8

"""
Platonus_API_Wrapper
~~~~~~~~~~~~~~~~~~~~
This library provides a very thin wrapper around the
Platonus REST API.
"""

import logging
import .exception
import pickle
from munch import munchify
from .request import RequestSessionWrapper, URLNormalizer

VERSION = "2.1"
BUILD_NUMBER = "101"
LICENCE_TYPE = "college"

logging.basicConfig(level=logging.INFO)

# Base API wrapper class
class PlatonusAPI(object):
    """
    Главный класс для работы с Платонус. Взаимодействие происходит на уровне REST API.
    Информации о REST API были получены путем обратной разработки веб приложении и Android клиента, так как в свободном доступе нету ни исходников Платонуса, ни документации (комерческая тайна).
    REST API Платонуса скорее всего работает на Java (но это не точно)
    Принимаемые аргументы:
        base_url - URL адресс Платонуса
        language - язык = ru - Русскии
                          kz - Казахскии
                          en - English
        context_path - корневой контекст URL адреса, где находится Платонус, обычно это /. К примеру колледж может на сайт example.kz установить Wordpress
            и вести там главную страницу колледжа, а Платонус поставить на example.kz/platonus, вот как раз /platonus является контекстом Платонуса.
            Более подробнее читайте здесь: https://medium.com/javascript-essentials/what-is-context-path-d442b3de164b
        check_API_compatibility - Проверка на совместимость данной библиотеки с Platonus сайтом.
    """

    def __init__(self, base_url: str, language: str = "ru", context_path: str = "/", check_api_compatibility: bool = True):
        platonus_url = URLNormalizer(base_url, context_path)
        self.session = RequestSessionWrapper(platonus_url)
        self.language = language
        self.auth_token = None
        if check_api_compatibility:
            self.check_compatibility_of_API_requests()

    def load_session(self, session_file: str):
        """
        Загружает сессию Платонуса из файла. Это позваляет каждый раз не логинится,
        достаточно залогинится, экспортировать сессию через save_session и в нужый момент зайти в сессию через load_session.
        ВНИМАНИЕ! У СЕСИИ ЕСТЬ ОПРЕДЕЛННЫЙ СРОК ДЕЙСТИИ, ПОКА НЕ ПОНЯТНО СКОЛЬКО ОНО ДЕЙСТВУЕТ, И КАК ЭТО ЗНАЧЕНИЕ ВЫСТАВЛЯЕТСЯ
        """
        with open(session_file, 'rb') as f:
            session, self.auth_token = pickle.load(f)
            self.session.load_session(session)

    def save_session(self, session_file: str):
        """
        Загружает сессию Платонуса в файл. Это позваляет каждый раз не логинится,
        достаточно залогинится, экспортировать сессию через save_session и в нужый момент зайти в сессию через load_session.
        ВНИМАНИЕ! У СЕСИИ ЕСТЬ ОПРЕДЕЛННЫЙ СРОК ДЕЙСТИИ, ПОКА НЕ ПОНЯТНО СКОЛЬКО ОНО ДЕЙСТВУЕТ, И КАК ЭТО ЗНАЧЕНИЕ ВЫСТАВЛЯЕТСЯ
        """
        with open(session_file, 'wb') as f:
            pickle.dump((self.session.save_session(), self.auth_token), f)

    def login(self, username: str = None, password: str = None, IIN: str = None):
        """
        Авторизация в Платонус
        Принимаемые аргументы:
            username - логин
            password - пароль
            IIN - ИИН
        """
        self._username = username
        self._password = password
        self._iin = IIN

        __auth_type = self.platonus_auth_type().value

        # Ждем с нетерпением нативный Switch-Case в Python 3.10, а то что-то мне не хочется плодить if-else =)
        if __auth_type == "1":
            if not username or not password or IIN:
                raise exception.NotCorrectLoginCredentials("Укажите только username/password значения для авторизации в Платонус")
        elif __auth_type == "2":
            if not username or not password or not IIN:
                raise exception.NotCorrectLoginCredentials("Укажите только username/password/IIN значения для авторизации в Платонус")
        elif __auth_type == "3":
            if username or not password or not IIN:
                raise exception.NotCorrectLoginCredentials("Укажите только password/IIN значения для авторизации в Платонус")
        elif __auth_type == "4":
            if username or password or IIN:
                raise exception.NotCorrectLoginCredentials("Для авторизации в Платонус не требуется ввод учетных данных")

        header = dict(language=self.language_num)
        params = dict(login=username, password=password, IIN=IIN)
        response = munchify(self.session.post('rest/api/login', json=params, headers=header).json())

        if response.login_status == "invalid":
            raise exception.NotCorrectLoginCredentials(response.message)

        # logging.info(f"Ваш авторизационный токен: {response.auth_token}")
        self.auth_token = response.auth_token
        return response

    def person_fio(self):
        """Возврашяет ФИО пользывателя"""
        response = self.session.get('rest/fio', headers={'token': self.auth_token})
        return response.text

    def person_picture(self):
        """Возврашяет аватарку пользывателя"""
        response = self.session.get('rest/img/profilePicture', stream=True)
        return response.content

    def person_type_list(self):
        """По идее должен возврящать список типов пользывателей Platonus, но плчему-то ничего не возвращяет, нафиг его тогда  реализовали?!"""
        response = self.session.get(f'rest/api/person/personTypeList/{self.language}').json()
        return munchify(response)

    def person_info(self):
        """
        Возврашяет информацию о пользывателе
        Возвращаемые значения:
            lastName - Фамилия
            firstName - Имя
            patronymic - Отчество
            personType - Тип пользывателя = 1 - ученик
                                            0 - учитель
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
        response = self.session.get(f'rest/mobile/personInfo/{self.language}', headers={'token': self.auth_token}).json()
        return munchify(response)

    def student_tasks(self, count_in_part, part_number, start_date, end_date, recipient_status, topic="", study_group_id="-1", subject_id="-1", tutor_id="-1", term="-1", year="-1"):
        """Возвращяет все задания ученика"""
        params = dict(countInPart=count_in_part, endDate=end_date, partNumber=part_number, recipientStatus=recipient_status, startDate=start_date, studyGroupID=study_group_id, subjectID=subject_id, term=term, topic=topic, tutorID=tutor_id, year=year)
        return self.session.post(f'rest/assignments/studentTasks/-1/{self.language_num}', headers={'token': self.auth_token}, json=params).json()

    def study_years_list(self):
        response = self.session.get(f'rest/mobile/student/studyYears/{self.language}', headers={'token': self.auth_token}).json()
        return munchify(response)

    def get_marks_by_date(self):
        response = self.session.get(f'assignments/assignedYears/{self.language}', headers={'token': self.auth_token}).json()
        return munchify(response)

    def terms_list(self):
        """Возвращяет список семестров"""
        response = self.session.get(f'rest/mobile/tutor/terms/{self.language}', headers={'token': self.auth_token}).json()
        return munchify(response)

    def student_journal(self, year: int, term: int):
        """
        Возвращяет журнал ученика
        Принимаемые аргументы: (см. также функцию study_years_list())
            year - год
            term - семестр
        """
        response = self.session.get(f'rest/api/journal/{year}/{term}/{self.language}', headers={'token': self.auth_token}).json()
        return munchify(response)

    def recipient_statuses_list(self):
        """Возвращяет список всех возможных статусов задании"""
        response = self.session.get(f'rest/assignments/recipientStatuses/{self.language_num}', headers={'token': self.auth_token}).json()
        return munchify(response)

    def platonus_icon(self, icon_size="small"):
        """
        Возврашяет иконку Плаонуса
        Принимаемые аргументы:
            icon_size = принимает размер иконки: small или big
        """
        response = self.session.get(f'img/platonus-logo-{icon_size}.png', stream=True)
        return response.content

    def platonus_server_time(self):
        """
        Возвращает текущее серверное время Плаонуса
        ВНИМАНИЕ: АДРЕС REST API МЕНЯЕТСЯ В РАЗНЫХ ВЕРСИЯХ ПЛАТОНУСА!
        Старый API REST URL: /menuTimeDate
        Возвращяемые значения:
            hour - час
            minute - минута
            date - дата
            dayOfWeek - день недели
        """
        response = self.session.get(f'rest/api/menu/menu_time_date/{self.language}').json()
        return munchify(response)

    def platonus_auth_type(self):
        """
        Возвращает тип авторизации в Платонус
        Возвращаемые значения:
            value = 1 - логин и пароль
                    2 - ИИН, логин и пароль
                    3 - ИИН и пароль
                    4 - ничего (?)
        """
        response = self.session.get('rest/api/authType').json()
        return munchify(response)

    def rest_api_information(self):
        """
        Возвращает данные об Платонусе
        Возвращаемые значения:
            productName - название продукта
            VERSION - версия Платонуса
            BUILD_NUMBER - версия билда Платонуса
            year - текущии код
            developerLink - ссылка на сайт разработчиков Платонуса
            developerName - группа разработчиков
            licenceType - тип лицензии = college - колледж
                                         university - университет
        """
        response = self.session.get('rest/api/version').json()
        return munchify(response)

    def has_module(self, module):
        """
        PROFILE = "student"
        JOURNAL = "studentregister"
        CURRENT_JOURNAL = "current_progress_gradebook_student"
        ASSIGNMENT = "assignment"
        STUDY_ROOM = "studyroom"
        """
        return module
        #response = self.session.get(f'api/person/hasModule/{module}', headers={'token': self.auth_token}).json()
        #return munchify(response)

    def check_compatibility_of_API_requests(self):
        """
        Проверяет совместимость данной библиотеки с Платонусом. Некоторые адреса REST API,
        а также передаваемые значения могут быть изменены в некоторых версиях Платонуса (например platonus_server_time())
        """
        rest_api_info = self.rest_api_information()

        api_compatibility_warn = "Это библиотека не была протестирована c текущей версии Платонуса! Используйте библиотеку на свой страх и риск"
        assert rest_api_info.BUILD_NUMBER == BUILD_NUMBER, api_compatibility_warn
        assert rest_api_info.VERSION == VERSION, api_compatibility_warn
        assert rest_api_info.licenceType == LICENCE_TYPE, f"This Platonus API Wraper dedicated for colleges, not for {rest_api_info['licenceType']}"

    @property
    def language_num(self):
        """
        Для того чтобы получить данные на определенном языке от Платонуса нужно отправить сокращенное
        имя языка (ru, kz, en), или же цифровые сокращение (1 - ru и т.д.). Это зависит какой запрос вы выполняете.
        И определенной закономерности этому нету. Я не понимаю, нафига одни запросы отправлять цифрами, а другие
        буквенными обозначениями?! И зачем нужен значение plt_lang в куках, для фронтенда?
        """
        if self.language == "ru":
            language = "1"
        elif self.language == "kz":
            language = "2"
        elif self.language == "en":
            language = "3"
        else:
            raise ValueError(f"Unsupported language: {self.language}")
        return language

    @property
    def is_authed(self):
        """Checks whether credentials were passed."""

        return True if self._username and self._password else False

    def logout(self):
        self.session.post('rest/api/logout/', headers={'token': self.auth_token})
