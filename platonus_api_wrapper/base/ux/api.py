from platonus_api_wrapper.const import LanguageCode
from platonus_api_wrapper.validators import language_code_to_int


class UiApiMethods:
    """Менеджер REST API методов Платонуса для UI-компонентов

    Args:
        language_code - название языка в стандарте ISO 639-1, к примеру: ru, kz, en
        rest_api_version - Принимает версию Платонуса.
    """

    def __init__(self, language_code: LanguageCode, rest_api_version: float):
        self.language_code_str = language_code
        self.language_code_int = language_code_to_int(language_code)
        self.rest_api_version = rest_api_version

        self.notifications = f"rest/systemMessages/false/{self.language_code_str}"
        self.survey_notifications = (
            f"rest/systemMessages/notification/{self.language_code_str}"
        )
        self.has_for_visually_impaired_license = (
            "rest/api/hasForVisuallyImpairedLicense"
        )
        self.system_messages_letters = (
            f"rest/systemMessages/letters/{self.language_code_str}"
        )
        self.get_messages_by_params = (
            f"rest/systemMessages/getMessagesByParams/{self.language_code_str}"
        )
        self.get_logo = "rest/login-page/get-logo"

    @property
    def has_unshown_release(self):
        return f"rest/releases/hasUnshownRelease?language={self.language_code_str}"
