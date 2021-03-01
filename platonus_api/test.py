from platonus_api import PlatonusAPI
import config
import time
from pprint import pprint

platonus_session = PlatonusAPI(platonus_url = config.BASE_PLATONUS_SITE_URL, language="kz", check_API_compatibility=True)
pprint(platonus_session.login(*config.PLATONUS_LOGIN_CREDITIONALS))
#platonus_session.load_session("session.pkl")
pprint(platonus_session.person_fio())
pprint(platonus_session.person_info())
pprint(platonus_session.platonus_server_time())
pprint(platonus_session.rest_api_information())
pprint(platonus_session.platonus_auth_type())
pprint(platonus_session.recipient_statuses_list())
pprint(platonus_session.study_years_list())
pprint(platonus_session.terms_list())
#platonus_session.save_session("session.pkl")
pprint(platonus_session.person_type_list())
pprint(platonus_session.student_tasks(count_in_part="20", part_number="0", recipient_status="2", start_date="10-01-2021", end_date="23-02-2021"))
platonus_session.logout()