import logging
from functools import wraps

from . import exceptions

logger = logging.getLogger("platonus_api_wrapper")

def login_required(method):
    """Make sure user is logged in before proceeding"""
    @wraps(method)
    def wrapper_login_required(self, *args, **kwargs):

        if not self.user_is_authed:
            raise exceptions.NotCorrectLoginCredentials(f"Метод '{method.__name__}' требует авторизацию, но вы не авторизовались в Платонус. Пожалуйста выполните метод login, и укажите авторизационные данные")

        if not self.auto_relogin:
            return method(self, *args, **kwargs)

        try:
            return method(self, *args, **kwargs)
        except exceptions.LoginSessionExpired:
            logger.warning("Login session is expired, reloging...")

            self.login(**self._auth_credentials)
            return method(self, *args, **kwargs)

    return wrapper_login_required

