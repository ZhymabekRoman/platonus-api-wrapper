from ..utils import exceptions


def ValidateLoginCredentials(auth_credentials, auth_type):
    """Проверяет, верно ли были заполнены авторизационные данные в соответствии с типом авторизации

    В Платонусе есть 4 типа авторизации: 
        1 тип) Логин/пароль
        2 тип) Логин/пароль/ИИН
        3 тип) Пароль/ИИН
        4 тип) Ничего (?)

    И во время ввода пользывателем авторизационные данные нужно проверять, а может он ввел ИИН когда нужно было ввести только Логин/пароль

    Args:
        auth_credentials: Принимает словарь, с авторизационными данными, который заранее был переведен в объект через dict2object.
        auth_type: Принимает тип авторизации от Платонуса
    Raises:
        NotCorrectLoginCredentials: Если пользыватель ввел лишние поля, или если наоборот какое-то поле не заполнено
    """
    login, password, IIN = auth_credentials.login, auth_credentials.password, auth_credentials.IIN

    # Ждем с нетерпением нативный Switch-Case в Python 3.10, а то что-то мне не хочется плодить if-else =)
    if auth_type == "1":
        if not login or not password or IIN:
            raise exceptions.NotCorrectLoginCredentials("Укажите только login/password значения для авторизации в Платонус")
    elif auth_type == "2":
        if not login or not password or not IIN:
            raise exceptions.NotCorrectLoginCredentials("Укажите только login/password/IIN значения для авторизации в Платонус")
    elif auth_type == "3":
        if login or not password or not IIN:
            raise exceptions.NotCorrectLoginCredentials("Укажите только password/IIN значения для авторизации в Платонус")
    elif auth_type == "4":
        if login or password or IIN:
            raise exceptions.NotCorrectLoginCredentials("Для авторизации в Платонус не требуется ввод учетных данных")
