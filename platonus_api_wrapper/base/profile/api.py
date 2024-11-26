from platonus_api_wrapper.const import LanguageCode
from platonus_api_wrapper.validators import language_code_to_int


class ProfileApiMethods:
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

        self.profile_picture = "rest/img/profilePicture"

        self.person_id = "rest/api/person/personID"
        self.is_admin = "rest/api/person/isAdmin"
        self.person_type = "rest/api/person/personType"
        self.student_state_info = (
            f"rest/api/person/studentStateInfo/{self.language_code_str}"
        )
        self.profile_info = f"rest/mobile/personInfo/{self.language_code_str}"
        self.system_messages_letters = (
            f"rest/systemMessages/letters/{self.language_code_str}"
        )
        self.person_type_list = (
            f"rest/api/person/personTypeList/{self.language_code_str}"
        )
        self.upload_profile_picture = "rest/file/uploadProfilePicture"

    @property
    def person_fio(self):
        if self.rest_api_version.version >= 7.0:
            return f"rest/fio/{self.language_code_str}"
        else:
            return "rest/fio"
