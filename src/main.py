#! /usr/bin/env python
# encoding: utf-8

"""
Platonus_API_Wrapper
~~~~~~~~~~~~~~~~~~~~
This library provides a very thin wrapper around the
Platonus REST API.
"""

import logging
import exception
import pickle
from request import RequestSessionWrapper
from pydantic.dataclasses import dataclass
from typing import List

__author__ = "Zhymabek Roman"
__version__ = "0.01a"
__license__ = "AGPL-3.0 License"

LOCALE = "ru" # Думаю нету смыла менять на kz/en, фиг поймеш что где как =)
VERSION = "2.1"
BUILD_NUMBER = 101
LICENCE_TYPE = "college"

logging.basicConfig(level=logging.INFO)

# ToDo - реализовать
#url = 'https://httpbin.org/post' # Set destination URL here
#post_fields = {'foo': 'bar'}     # Set POST fields here

# Base API wrapper class
class PlatonusAPI(object):
    """
    Главный класс для работы с Платонус. Взаимодействие происходит на уровне REST API. 
    Информации о REST API были получены путем обратной разработки веб приложении и Android клиента, так как в свободном доступе нету ни исходников Платонуса, ни документации (комерческая тайна).
    Кстати говоря, REST API Платонуса скорее всего работает на Java (но это не точно)
    """
    #__slots__ = ('platonus_url', 'auth_token', 'check_compatibility', 'session')
    
    def __init__(self, platonus_url, check_compatibility: bool = True):
        self.platonus_url = platonus_url
        self.auth_token = None # ToDo - not working
        self.check_compatibility = check_compatibility

        self.session = RequestSessionWrapper(self.platonus_url)
        
        if self.check_compatibility:
            self.__check_compatibility_of_API_requests()

    def load_session(self, cookies_file): # ToDo
        with open(cookies_file, 'rb') as f:
            coockies_file_session, self.auth_token = pickle.load(f)
            self.session.load_cookies(coockies_file_session)

    def save_session(self, cookies_file): #ToDo
        print(f"Request returned cookies: {self.session.return_cookies()}")
        with open(cookies_file, 'wb') as f:
            pickle.dump((self.session.return_cookies(), self.auth_token), f)

    def login(self, username: str, password: str, IIN: str = "null"):
        @dataclass
        class response_fields:
            login_status: str
            auth_token: str = None
            personID: int = None
            personType: int = None
            message: str = None
            
        # Ждем с нетерпением нативный Switch-Case в Python 3.10, а то что-то мне не хочется плодить if-else =)
        auth_type = self.__auth_type()
        # ToDo
        if auth_type == 1:
            pass
        elif auth_type == 2:
            pass
        elif auth_type == 3:
            pass
        elif auth_type == 4:
            pass

        response = response_fields(**self.session.post('/rest/api/login', json={"login":username, "iin" :IIN, "password":password}).json())
        
        if response.login_status == "invalid":
            logging.warning("Your password or username seems is not correct!")
            raise exception.NotCorrectLoginCredentials(response.message)
        
        #logging.info(f"Ваш авторизационный токен: {response.auth_token}")
        self.auth_token = response.auth_token
    
    def persion_fio(self):
        response = self.session.get('/rest/fio', headers={'token': self.auth_token})
        return response.text
    
    def person_picture(self):
        response = self.session.get(f'{self.session}/rest/img/profilePicture', stream=True)
        return response.content
        
    def person_info(self):
        @dataclass
        class response_fields:
            lastName: str
            firstName: str
            patronymic: str
            personType: int
            photoBase64: str
            passwordExpired: bool
            temporaryPassword: bool
            studentID: int
            gpa: str
            courseNumber: int
            groupName: str
            professionName: str
            specializationName: str
            studyTechnology: int
            
        return response_fields(**self.session.get('/rest/mobile/personInfo/ru', headers={'token': self.auth_token}).json())
           
    def student_tasks(self, start_date , end_date, recipient_status):
        @dataclass
        class student_tasks_list:
            assignmentID: int
            topic: str
            startDate: str
            endDate: str
            files: List
            recipients: dict
            studyGroups: dict
            year: str
            term: str
            isDraft: str
            assessmentProvided: str
            showRecipients: str
            status: str
            statusName: str
            tutorName: str
            studyGroupName: str
            studyGroupID: str
            mainStudyGroupID: str
            isMain: str
            studentID: str
            assessment: str
            assessmentWeek: str
            assignmentRecipientID: str
            doneRecipientIDs: dict
            markID: str
            oldMarkID: str
            isCurrentMark: str
            tutorID: str
            hasAccess: str
            totalUnreadAnswers: str
            unreadAnswers: str
            markTypeName: str
            isDeletable: str
            markTypeID: str
            cipher: str
            moduleName: str
            subjectName: str
            isPractice: str
            considerTime: int
            immediatelyStart: int
            assignedDate: str = None
            oldEndDate: str = None
            assignmentText: str = None
            umks: dict = None
            cases: dict = None
            ktp: str = None
            justification: str = None
            assessmentMarkDate: str = None
            assessmentSymbol: str = None
            recipientName: str = None
            senderName: str = None
            inProgressStats: str = None
            pair: str = None
            theme: int = None
            startTime: int = None
            finishTime: int = None
            startTimeStr: int = None
            finishTimeStr: int = None
            controlWorkDate: int = None
            markName: str = None
            groupp: str = None

        @dataclass
        class response:
            total: int
            studentTasks: List[student_tasks_list]

        return response_fields(**self.session.post('/rest/assignments/studentTasks/-1/1', headers={'token': self.auth_token}, json={"countInPart": "1000", "endDate": end_date, "partNumber": "0", "recipientStatus": recipient_status, "startDate": start_date, "studyGroupID": "-1", "subjectID": "-1", "term": "-1", "topic": "", "tutorID": "-1", "year": "-1"}).json())

    def student_journal(self):
        @dataclass
        class exams_list:
            name: str
            mark: str
            markTypeId: int

        @dataclass
        class response_fields:
            subjectName: str
            totalMark: str
            centerMark: int
            color: str
            box_height: str
            subjectID: int
            exams: List[exams_list]

        # XXX - fixing dictionary iteration
        return response_fields(**self.session.get('/rest/api/journal/2020/2/ru', headers={'token': self.auth_token}).json()[0])
       
    def recipient_statuses_list(self):
        @dataclass
        class recipients_list:
            name: str
            ID: int

        @dataclass
        class response_fields:
            recipientStatuses: List[recipients_list]
                
        return response_fields(**self.session.get('/rest/assignments/recipientStatuses/1',  headers={'token': self.auth_token}).json())

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
        """
        @dataclass
        class response_fields:
            hour: int
            minute: int
            date: str
            dayOfWeek: str

        return response_fields(**self.session.get('/rest/api/menu/menu_time_date/ru').json())
    
    def __auth_type(self):
        """
        Возвращает тип авторизации в Платонус
        Возвращаемые значения:
            value = 1 - логин и пароль
                    2 - ИИН, логин и пароль
                    3 - ИИН и пароль
                    4 - ничего (?)
        """
        @dataclass
        class response_fields:
            value: int
        
        return response_fields(**self.session.get('/rest/api/authType').json())
    
    def __rest_api_information(self):
        """
        Возвращает данные об Платонусе
        """
        @dataclass
        class response_fields:
            productName: str
            VERSION: str
            BUILD_NUMBER: int
            year: int
            developerLink: str
            developerName: str
            licenceType: str
            
        return response_fields(**self.session.get('/rest/api/version').json())
    
    def __check_compatibility_of_API_requests(self):
        rest_api_info = self.__rest_api_information()

        assert rest_api_info.BUILD_NUMBER == BUILD_NUMBER, "This API wrapper seems is outdated! Please check API requests!"
        assert rest_api_info.VERSION == VERSION, "This API wrapper seems is outdated! Please check API requests!"
        assert rest_api_info.licenceType == LICENCE_TYPE, f"This Platonus API Wraper dedicated for colleges, not for {rest_api_info.licenceType}"
        
    def logout(self):
        request = self.session.post('/rest/api/logout/', headers={'token': self.auth_token})