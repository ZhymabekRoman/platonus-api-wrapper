import logging
import config
from exceptions import NotCorrectLoginCredentials
from request import RequestSessionWrapper
from dataclasses import dataclass

logging.basicConfig(level=logging.DEBUG)

@dataclass
class PlatonusAPI:
    platonus_url: str = None
    
    auth_token: str = None
    person_ID: int = None
    person_type: int = None
    
    check_compatibility: bool = True
    
    def __post_init__(self):
        self.session = RequestSessionWrapper(self.platonus_url, max_request_retries=3)
        
        if self.check_compatibility:
            self.check_compatibility_of_API_requests()

    def login(self, username: str, password: str):
        
        @dataclass
        class response:
            login_status: str
            auth_token: str = None
            personID: int = None
            personType: int = None
            message: str = None
            
        response = response(**self.session.post(f'{config.BASE_PLATONUS_SITE_URL}/rest/api/login', json={"login":username,"password":password}).json())
        
        if response.login_status == "invalid":
            logging.warning("Your password or username seems is not correct!")
            raise NotCorrectLoginCredentials(response.message)
            
        self.auth_token = response.auth_token
        self.person_ID = response.personID
        self.person_type = response.personType
    
    def persion_fio(self):
        
        response = self.session.get(f'{self.platonus_url}/rest/fio', headers={'token': self.auth_token})
        return response.text
    
    def person_picture(self):
        
        response = self.session.get(f'{self.session}/rest/img/profilePicture', stream=True)
        return response #ToDo - .content
        
    def person_info(self):
        
        @dataclass
        class response:
            lastName: str
            firstName: str
            patronymic: str
            personType: int
            photoBase64: str
            passwordExpired: bool
            temporaryPassword: bool
            studentID: int
            gpa: int
            courseNumber: int
            groupName: str
            professionName: str
            specializationName: str
            studyTechnology: int
            
        response = response(**self.session.get(f'{config.BASE_PLATONUS_SITE_URL}/rest/mobile/personInfo/ru', headers={'token': self.auth_token}).json())
        return response
           
#    def student_tasks(self):
#        response = self.session.post(f'{config.BASE_PLATONUS_SITE_URL}/rest/assignments/studentTasks/-1/1', headers={'token': self.auth_token}, json={"countInPart": "1000", "endDate": "31-12-2020", "partNumber": "0", "recipientStatus": "7", "startDate": "22-11-2020", "studyGroupID": "-1", "subjectID": "-1", "term": "-1", "topic": "", "tutorID": "-1", "year": "-1"})
#        user_info = response.json()
#        return user_info
#    
#    def student_journal(self):
#        
#        @dataclass
#        class response:
#            subjectName: str
#            totalMark: int
#            centerMark: int
#            color: str
#            box_height: str
#            subjectID: int
#    "exams": [
#      {
#        "name": "Ср.тек.",
#        "mark": "0",
#        "markTypeId": 6
#      },
#      {
#        "name": "ДЗ",
#        "mark": "-",
#        "markTypeId": 12
#      }
#    ]
#        
#        respons = self.session.get(f'{self.platonus_url}/rest/api/journal/2020/2/ru', headers={'token': self.auth_token}).json()
#        for each in respons:
#            response(**each)
#        return response
#        
    def recipient_statuses_list(self):
        response = self.session.get(f'{config.BASE_PLATONUS_SITE_URL}/rest/assignments/recipientStatuses/1')
        recipient_statuses = response.json()
        return recipient_statuses

    def platonus_icon(self):
        
        response = self.session.get(f'{self.platonus_url}/img/platonus-logo-small.png', stream=True)
        return response #ToDo - .content
        
    def platonus_server_time(self):
        
        @dataclass
        class response:
            hour: int
            minute: int
            date: str
            dayOfWeek: str
  
        response = response(**self.session.get(f'{config.BASE_PLATONUS_SITE_URL}/rest/api/menu/menu_time_date/ru').json())
        return response
    
    def platonus_auth_type(self):
        
        @dataclass
        class response:
            value: int
        
        response = response(**self.session.get(f'{config.BASE_PLATONUS_SITE_URL}/rest/api/authType').json())
        return response
    
    def platonus_rest_api_information(self):
        
        @dataclass
        class response:
            productName: str
            VERSION: str
            BUILD_NUMBER: int
            year: int
            developerLink: str
            developerName: str
            licenceType: str
            
        response = response(**self.session.get(f'{config.BASE_PLATONUS_SITE_URL}/rest/api/version').json())
        return response
    
    def check_compatibility_of_API_requests(self):
        rest_api_info = self.platonus_rest_api_information()
        
        assert rest_api_info.BUILD_NUMBER == 60 or rest_api_info.VERSION == 2.1, "This API wrapper seems is outdated! Please check API requests!"
        assert rest_api_info.licenceType =="college", f"This Platonus API Wraper dedicated for colleges, not for {rest_api_info.licenceType}"
        
     # XXX: 500 - INTERNAL SERVER ERROR
#    def logout(self):
#        #response = self.session.get(f'{self.platonus_url}/exit')
#        reguest = self.session.post(f'{self.platonus_url}/rest/api/logout/')
    
platonus_session = PlatonusAPI(config.BASE_PLATONUS_SITE_URL, check_compatibility=False)
platonus_session.login(*config.PLATONUS_LOGIN_CREDITIONALS)
print(platonus_session.platonus_server_time())
#print(platonus_session.person_info())
#print(platonus_session.platonus_auth_type())
#print(platonus_session.student_journal())
print(platonus_session.persion_fio())