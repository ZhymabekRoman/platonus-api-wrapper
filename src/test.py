from main import PlatonusAPI
from munch import munchify
import config
import time

platonus_session = PlatonusAPI(platonus_url = config.BASE_PLATONUS_SITE_URL, check_API_compatibility=True, json_output=False)
platonus_session.login(*config.PLATONUS_LOGIN_CREDITIONALS)
print(platonus_session.person_fio())
print(platonus_session.person_info())
print(platonus_session.platonus_server_time())
#print(munchify(platonus_session.platonus_server_time).hour)
print(platonus_session.rest_api_information())
print(platonus_session.platonus_auth_type())
print(platonus_session.recipient_statuses_list())
print(platonus_session.student_tasks(count_in_part="20", part_number="0", recipient_status="2", start_date="10-01-2021", end_date="28-02-2021", topic="Б.Байкадамов"))
platonus_session.logout()