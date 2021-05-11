from ..utils import exceptions


def ValidateLanguage(language_code: str):
    """Проверяет код языка, поддерживается ли он Платонусом
    Args:
        language_code (str): код языка в стандарте ISO 639-1, подробнее: https://ru.wikipedia.org/wiki/ISO_639-1 . К примеру: ru, en, kz
    Raises:
        UnsupportedLanguageCode: Если код языка не корректен или язык не поддерживается Платонусом
    Returns:
        bool: True если язык поддерживается Платонусом
    """
    supported_languages_code_list = ["ru", "en", "kz"]

    if language_code not in supported_languages_code_list:
        raise exceptions.UnsupportedLanguageCode(f"Язык {language_code} не поддерживается Платонусом. Поддерживаемые языки: {supported_languages_code_list}")

    return True


def LanguageCodeToInt(language_code: str):
    """Переводит код языка в цифры, которые понятны только Платонусу
    Args:
        language_code (str): код языка в стандарте ISO 639-1, подробнее: https://ru.wikipedia.org/wiki/ISO_639-1 . К примеру: ru, en, kz
    Raises:
        UnsupportedLanguageCode: Если код языка не корректен или язык не поддерживается Платонусом
    Returns:
        Код языка в цифрах, которая понятна только Платонусу. Требуется во время отправки запросов в Платонус
    """
    if language_code == "ru":
        return "1"
    elif language_code == "kz":
        return "2"
    elif language_code == "en":
        return "3"
    else:
        raise exceptions.UnsupportedLanguageCode(f"Язык {language_code} не поддерживается Платонусом.")
