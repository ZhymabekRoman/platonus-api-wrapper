from ..utils import exceptions

def ValidateLanguage(language_code):
    supported_languages_code_list = ["ru", "en", "kz"]

    if language_code not in supported_languages_code_list:
        raise exceptions.UnsupportedLanguageCode(f"Язык {language_code} не поддерживается Платонусом. Поддерживаемые языки: {supported_languages_code_list}")

def LanguageCodeToInt(language_code):
    if language_code == "ru":
        return "1"
    elif language_code == "kz":
        return "2"
    elif language_code == "en":
        return "3"
    else:
        raise exceptions.UnsupportedLanguageCode(f"Язык {language_code} не поддерживается Платонусом.")

