from platonus_api_wrapper import PlatonusAPI
from pprint import pprint

input_url = input("Введите адрес Платонус сайта: ")
platonus_session = PlatonusAPI(platonus_url=input_url, language="ru", check_API_compatibility=True)
auth_type = platonus_session.platonus_auth_type().value

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


pprint(platonus_session.login(username=input_username, password=input_pswd, IIN=input_IIN))
# platonus_session.load_session("session.pkl")
pprint(platonus_session.person_fio())
pprint(platonus_session.person_info())
pprint(platonus_session.platonus_server_time())
pprint(platonus_session.rest_api_information())
pprint(platonus_session.platonus_auth_type())
pprint(platonus_session.recipient_statuses_list())
pprint(platonus_session.study_years_list())
pprint(platonus_session.terms_list())
# platonus_session.save_session("session.pkl")
pprint(platonus_session.person_type_list())
pprint(platonus_session.student_tasks(count_in_part="20", part_number="0", recipient_status="2", start_date="10-01-2021", end_date="23-02-2021"))
platonus_session.logout()
