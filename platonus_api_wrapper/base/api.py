from ..validators import LanguageCodeToInt


class Methods:
    """Менеджер REST API методов Платонуса

    Менеджер нужен:
    Во первых, в разных версиях Платонуса некоторые адреса REST API менялись, и соотвественно нужно учитовать во время отправки запросов
    Во вторых, во время отправки запросов отправляется язык, в котором должен быть запрос/ответ в/от Платонус.

    Вообще, кстати говоря, не понятно, почему в некоторых запросах для указывания языка используются коды языков (ru, en, ru) а в других - цифры (1, 2, 3), закономерность которых установлено Платонусом. 

    Args:
        language_code - Сокращенные двухзначные названия стран, см: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2 . К примеру: ru, kz, en
        rest_api_version - Принимает версию Платонуса.
    """
    def __init__(self, language_code, rest_api_version):
        self.language_code_str = language_code
        self.language_code_int = LanguageCodeToInt(language_code)
        self.rest_api_version = rest_api_version

        self.login = "rest/api/login"
        self.logout = "rest/api/logout"

        self.auth_type = "rest/api/authType"

        self.person_fio = "rest/fio"
        self.person_id = "rest/api/person/personID"
        self.profile_info = f'rest/mobile/personInfo/{self.language_code_str}'
        self.profile_picture = "rest/img/profilePicture"

        self.person_type_list = f"rest/api/person/personTypeList/{self.language_code_str}"
        self.student_tasks = f'rest/assignments/studentTasks/-1/{self.language_code_int}'
        self.study_years_list = f'rest/mobile/student/studyYears/{self.language_code_str}'
        self.terms_list = f'rest/mobile/tutor/terms/{self.language_code_str}'
        self.get_marks_by_date = f'assignments/assignedYears/{self.language_code_str}'
        self.recipient_statuses_list = f'rest/assignments/recipientStatuses/{self.language_code_int}'

    @property
    def server_time(self):
        if self.rest_api_version.version <= 2.0 or self.rest_api_version.version >= 5.0:
            return "menuTimeDate"
        else:
            return f"rest/api/menu/menu_time_date/{self.language_code_str}"

    def recipient_task_info(self, recipient_task_id):
        return f"rest/assignments/tutor/assignment/loadRecipientTaskInfo/{self.language_code_int}?assignmentRecipientID={recipient_task_id}"

    def student_journal(self, year: int, term: int):
        return f"rest/api/journal/{year}/{term}/{self.language_code_str}"

    def has_module(self, module_name):
        return f"rest/api/person/hasModule/{module_name}"
