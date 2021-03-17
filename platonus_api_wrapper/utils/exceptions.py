
class UnknownError(Exception):
    pass

class NotCorrectLoginCredentials(Exception):
    pass

class ServerError(Exception):
    pass

class LoginSessionExpired(Exception):
    pass

class InvalidURL(Exception):
    pass

class UnsupportedLanguageCode(Exception):
    pass

class TimedOut(Exception):
    pass

class NetworkError(Exception):
    pass

class NotValidJSON(Exception):
    pass
