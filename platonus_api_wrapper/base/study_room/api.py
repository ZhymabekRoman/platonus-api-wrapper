from platonus_api_wrapper.const import LanguageCode
from platonus_api_wrapper.validators import language_code_to_int


class StudyRoomApi:
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

        self.report_without_appeal = (
            f"rest/api/journal/reports/without-appeal/{self.language_code_str}"
        )

    def student_journal(self, year: int, term: int):
        return f"rest/api/journal/{year}/{term}/{self.language_code_str}"

    def student_journal_records(self, year: int, term: int, subject_id: int):
        return f"rest/mobile/journal/records/{year}/{term}?subjectID={subject_id}"
