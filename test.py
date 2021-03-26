import logging
from platonus_api_wrapper import PlatonusAPI
from pprint import pprint

logging.basicConfig(level=logging.DEBUG)

input_url = input("Введите адрес Платонус сайта: ")
platonus_session = PlatonusAPI(base_url=input_url, language="ru")
auth_type = platonus_session.auth_type().value

if auth_type == "1":
    input_IIN = None
    input_username = input("Введите логин: ")
    input_pswd = input("Введите пароль: ")
elif auth_type == "2":
    input_IIN = input("Введите ИИН: ")
    input_username = input("Введите логин: ")
    input_pswd = input("Введите пароль: ")
elif auth_type == "3":
    input_IIN = input("Введите ИИН: ")
    input_username = None
    input_pswd = input("Введите пароль: ")
elif auth_type == "4":
    input_IIN = None
    input_username = None
    input_pswd = None


pprint(platonus_session.login(login=input_username,
       password=input_pswd, IIN=input_IIN))
# platonus_session.load_session("session.pkl")
pprint(platonus_session.person_fio())
pprint(platonus_session.person_info())
pprint(platonus_session.server_time())
pprint(platonus_session.rest_api_information())
pprint(platonus_session.auth_type())
pprint(platonus_session.recipient_statuses_list())
pprint(platonus_session.study_years_list())
pprint(platonus_session.terms_list())
# platonus_session.save_session("session.pkl")
pprint(platonus_session.person_type_list())
pprint(platonus_session.student_tasks(countInPart="20", partNumber="0",
       recipientStatus="2", startDate="10-01-2021", endDate="23-02-2021"))
platonus_session.logout()
