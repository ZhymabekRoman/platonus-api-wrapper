#! /usr/bin/env python
# encoding: utf-8

"""
Platonus_API_Wrapper
~~~~~~~~~~~~~~~~~~~~
This library provides a very thin wrapper around the
Platonus REST API.
"""

import logging
import json
import exception
#import pickle
from munch import munchify
from request import RequestSessionWrapper

LOCALE = "ru" # Думаю нету смыла менять на kz/en, фиг поймеш что где как =)
VERSION = "2.1"
BUILD_NUMBER = "101"
LICENCE_TYPE = "college"

logging.basicConfig(level=logging.INFO)

# Base API wrapper class
class PlatonusAPI(object):
    """
    Главный класс для работы с Платонус. Взаимодействие происходит на уровне REST API. 
    Информации о REST API были получены путем обратной разработки веб приложении и Android клиента, так как в свободном доступе нету ни исходников Платонуса, ни документации (комерческая тайна).
    Кстати говоря, REST API Платонуса скорее всего работает на Java (но это не точно)
    """
    def __init__(self, platonus_url, check_API_compatibility: bool = True, json_output: bool =False):
        self.session = RequestSessionWrapper(platonus_url)
        if check_API_compatibility:
            self.check_compatibility_of_API_requests()
        #self.json_output = json_output #ToDO

#    def load_session(self, cookies_file): # ToDo
#        with open(cookies_file, 'rb') as f:
#            coockies_file_session, self.auth_token = pickle.load(f)
#            self.session.load_cookies(coockies_file_session)

#    def save_session(self, cookies_file): #ToDo
#        print(f"Request returned cookies: {self.session.return_cookies()}")
#        with open(cookies_file, 'wb') as f:
#            pickle.dump((self.session.return_cookies(), self.auth_token), f)

    def login(self, username  = None, password  = None, IIN = None):

        auth_type = self.platonus_auth_type()['value']

        # Ждем с нетерпением нативный Switch-Case в Python 3.10, а то что-то мне не хочется плодить if-else =)
        if auth_type == "1":
            if not username or not password or IIN:
                raise exception.NotCorrectLoginCredentials("Укажите только login/password значения для авторизации в Платонус")
        elif auth_type == "2":
            if not username or not password or not IIN:
                raise exception.NotCorrectLoginCredentials("Укажите только login/password/IIN значения для авторизации в Платонус")
        elif auth_type == "3":
            if username or not password or not IIN:
                raise exception.NotCorrectLoginCredentials("Укажите только password/IIN значения для авторизации в Платонус")
        elif auth_type == "4":
            if username or password or IIN:
                raise exception.NotCorrectLoginCredentials("Для авторизации в Платонус не требуется ввод учетных данных")
        
        params = dict(login=username, password=password, IIN=IIN)
        response = self.session.post('/rest/api/login', json=params).json()
        
        if response['login_status'] == "invalid":
            raise exception.NotCorrectLoginCredentials(response.message)
        
        logging.info(f"Ваш авторизационный токен: {response['auth_token']}")
        self.auth_token = response['auth_token']
    
    def person_fio(self):
        """Возврашяет ФИО пользывателя"""
        response = self.session.get('/rest/fio', headers={'token': self.auth_token})
        return response.text
    
    def person_picture(self):
        response = self.session.get(f'{self.session}/rest/img/profilePicture', stream=True)
        return response.content
        
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
        return self.session.get('/rest/mobile/personInfo/ru', headers={'token': self.auth_token}).json()

    def student_tasks(self, count_in_part, part_number, start_date, end_date, recipient_status, topic = "", study_group_id = "-1", subject_id = "-1", tutor_id = "-1", term = "-1", year = "-1"):
        params = dict(countInPart=count_in_part, endDate=end_date, partNumber=part_number, recipientStatus=recipient_status, startDate=start_date, studyGroupID=study_group_id, subjectID=subject_id, term=term, topic=topic, tutorID=tutor_id, year=year)
        return self.session.post('/rest/assignments/studentTasks/-1/1', headers={'token': self.auth_token}, json=params).json()

    def student_journal(self):

        return self.session.get('/rest/api/journal/2020/2/ru', headers={'token': self.auth_token}).json()
       
    def recipient_statuses_list(self):

        return self.session.get('/rest/assignments/recipientStatuses/1',  headers={'token': self.auth_token}).json()

    def platonus_icon(self, icon_size = "small"):
        """
        Возврашяет иконку Плаонуса
        Принимаемые аргументы:
            icon_size = принимает размер иконки: small или big
        """
        response = self.session.get(f'/img/platonus-logo-{icon_size}.png', stream=True)
        return response.content
        
    def platonus_server_time(self):
        """
        Возвращает серверное время Плаонуса
        ВНИМАНИЕ: АДРЕС REST API МЕНЯЕТСЯ В РАЗНЫХ ВЕРСИЯХ ПЛАТОНУСА!
        Старый API REST URL: /menuTimeDate
        """
        return self.session.get('/rest/api/menu/menu_time_date/ru').json()
    
    def platonus_auth_type(self):
        """
        Возвращает тип авторизации в Платонус
        Возвращаемые значения:
            value = 1 - логин и пароль
                    2 - ИИН, логин и пароль
                    3 - ИИН и пароль
                    4 - ничего (?)
        """
        return self.session.get('/rest/api/authType').json()
    
    def rest_api_information(self):
        """
        Возвращает данные об Платонусе
        """
        return self.session.get('/rest/api/version').json()
            
    def check_compatibility_of_API_requests(self):
        """
        Проверяет совместимость данной библиотеки с Platonus сайтом. Некоторые адреса REST API,
        а также передаваемые значения могут быть изменены в некоторых версиях Платонуса (например platonus_server_time())
        """
        rest_api_info = self.rest_api_information()

        api_compatibility_warn = "Это библиотека не была протестирована c текущей версии сайта Платонуса! Используйте библиотеку на свой страх и риск"
        assert rest_api_info['BUILD_NUMBER'] == BUILD_NUMBER, api_compatibility_warn
        assert rest_api_info['VERSION'] == VERSION, api_compatibility_warn
        assert rest_api_info['licenceType'] == LICENCE_TYPE, f"This Platonus API Wraper dedicated for colleges, not for {rest_api_info['licenceType']}"
        
    def logout(self):
        self.session.post('/rest/api/logout/', headers={'token': self.auth_token})