from typing import Literal

from ..const import LanguageCode, LANGUAGE_MAPPING, SUPPORTED_LANGUAGES
from ..utils import exceptions


def validate_language(language_code: LanguageCode) -> bool:
    """Проверяет код языка, поддерживается ли он Платонусом
    Args:
        language_code (str): код языка в стандарте ISO 639-1, подробнее: https://ru.wikipedia.org/wiki/ISO_639-1 . К примеру: ru, en, kz
    Raises:
        UnsupportedLanguageCode: Если код языка не корректен или язык не поддерживается Платонусом
    Returns:
        bool: True если язык поддерживается Платонусом
    """
    if language_code not in SUPPORTED_LANGUAGES:
        raise exceptions.UnsupportedLanguageCode(
            f"Language {language_code} is not supported by Platonus. Supported languages: {SUPPORTED_LANGUAGES}"
        )
    return True


def language_code_to_int(language_code: LanguageCode) -> str:
    """Переводит код языка в цифры, которые понятны только Платонусу
    Args:
        language_code (str): код языка в стандарте ISO 639-1, подробнее: https://ru.wikipedia.org/wiki/ISO_639-1 . К примеру: ru, en, kz
    Raises:
        UnsupportedLanguageCode: Если код языка не корректен или язык не поддерживается Платонусом
    Returns:
        Код языка в цифрах, которая понятна только Платонусу. Требуется во время отправки запросов в Платонус
    """
    validate_language(language_code)
    return LANGUAGE_MAPPING[language_code]
