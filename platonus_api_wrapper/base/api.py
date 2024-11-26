from typing import Literal

from ..const import LanguageCode
from ..validators import language_code_to_int


class ApiMethods:
    """Менеджер REST API методов Платонуса

    Менеджер нужен:
    Во первых, в разных версиях Платонуса некоторые адреса REST API менялись, и соотвественно нужно учитовать во время отправки запросов
    Во вторых, во время отправки запросов отправляется язык, в котором должен быть запрос/ответ в/от Платонус.

    Вообще, кстати говоря, не понятно, почему в некоторых запросах для указывания языка используются коды языков (ru, en, ru) а в других - цифры (1, 2, 3), закономерность которых установлено Платонусом.

    Args:
        language_code - название языка в стандарте ISO 639-1, к примеру: ru, kz, en
        rest_api_version - Принимает версию Платонуса.
    """

    def __init__(self, language_code: LanguageCode, rest_api_version: float):
        self.language_code_str = language_code
        self.language_code_int = language_code_to_int(language_code)
        self.rest_api_version = rest_api_version

        self.login = "rest/api/login"
        self.logout = "rest/api/logout"

        self.auth_type = "rest/api/authType"

        self.student_tasks = (
            f"rest/assignments/studentTasks/-1/{self.language_code_int}"
        )
        self.study_years_list = (
            f"rest/mobile/student/studyYears/{self.language_code_str}"
        )
        self.terms_list = f"rest/mobile/tutor/terms/{self.language_code_str}"
        self.get_marks_by_date = f"assignments/assignedYears/{self.language_code_str}"
        self.recipient_statuses_list = (
            f"rest/assignments/recipientStatuses/{self.language_code_int}"
        )

        self.applicant_reg_degrees = (
            f"rest/api/applicant_reg_degrees?lang={self.language_code_int}"
        )

        self.citizenship_list = (
            f"rest/api/citizenship_list?lang={self.language_code_int}"
        )

    @property
    def server_time(self):
        if self.rest_api_version.version <= 2.0 or self.rest_api_version.version >= 5.0:
            return "menuTimeDate"
        else:
            return f"rest/api/menu/menu_time_date/{self.language_code_str}"

    def recipient_task_info(self, recipient_task_id):
        return f"rest/assignments/tutor/assignment/loadRecipientTaskInfo/{self.language_code_int}?assignmentRecipientID={recipient_task_id}"

    def has_module(self, module_name: str):
        return f"rest/api/person/hasModule/{module_name}"

    def has_module_license(self, module_name: str):
        return f"rest/moduleLicense/by_module/{module_name}"

    def university_application_types(self, degree_id: int | Literal[""] = ""):
        return f"rest/api/university_application_types?lang={self.language_code_int}&degreeID={degree_id}"
