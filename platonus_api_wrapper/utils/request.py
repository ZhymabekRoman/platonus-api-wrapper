import logging
import requests
from . import exceptions
from requests.adapters import HTTPAdapter

logging.getLogger('urllib3').setLevel(logging.WARNING)

logger = logging.getLogger("platonus_api_wrapper")

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4240.198 Safari/537.36 OPR/72.0.3815.459', 'Content-Type': 'application/json; charset=UTF-8'}

class RequestSessionWrapper:
    """
    Вспомогательный класс, для работы с POST и GET запросами.
    Args:
        base_url: корневой адресс сайта
        proxy_dict: словарь прокси серверов
        timeout: устанавливает таймаут на запросы
        request_retries: количество попыток после неудачного соединения
        ssl_verify: позволяет верифицировать SSL-сертификаты для HTTPS-запросов так же, как и браузер
    """
    def __init__(self, base_url, proxy_dict={}, timeout=10.0, request_retries=3, ssl_verify=False):
        self.base_url = base_url
        self.proxies = proxy_dict
        self.timeout = timeout
        self.verify = ssl_verify

        __adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=request_retries)

        self.__session = requests.Session()
        self.__session.headers.update(HEADER)
        self.__session.mount(base_url, __adapter)

    def request(self, method, url, data, *args, **kwargs):
        try:
            response = self.__session.request(method, url=f"{self.base_url}{url}", json=data, timeout=self.timeout, proxies=self.proxies, verify=self.verify, *args, **kwargs)
            response.encoding = 'utf-8'
        except requests.Timeout:
            raise exceptions.TimedOut()
        except (requests.RequestException, requests.exceptions.ConnectionError) as e:
            raise exceptions.NetworkError(e)
        else:
            logger.debug(f"URL: {self.base_url}{url}, status code: {response.status_code}, {method} response contetnt: {response.content}")

            self._raise_by_status_code(response.status_code)

            return response

    def _raise_by_status_code(self, status_code):
        if (
            status_code != 401
            and status_code >= 402
            and status_code <= 500
            or status_code == 404
        ):
            raise exceptions.ServerError(f"Серверная ошибка, попробуйте чуть позже, код ошибки: {status_code}")

        elif status_code == 401:
            raise exceptions.LoginSessionExpired("Сессия истекла, возобновите сессию с помощью метода login")

    def post(self, url, data=None, *args, **kwargs):
        logger.debug(f"URL: {url}, POST request")
        return self.request('POST', url, data, *args, **kwargs)

    def get(self, url, data=None, *args, **kwargs):
        logger.debug(f"URL: {url}, GET request")
        return self.request('GET', url, data, *args, **kwargs)

    @property
    def request_session(self):
        return self.__session

    @request_session.setter
    def request_session(self, session):
        self.__session = session

    @property
    def request_header(self):
        return self.__session.header

    @request_header.setter
    def request_header(self, header_value):
        for key, value in header_value.items():
            if value is None:
                self.__session.headers.pop(key)
            else:
                self.__session.headers.update(header_value)

    def __dell__(self):
        self.__session.close()


__all__ = [RequestSessionWrapper]
