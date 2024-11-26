import json
import logging

import requests
from requests.adapters import HTTPAdapter

from ..utils.dict2object import dict2object
from . import exceptions

logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger("platonus_api_wrapper")

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4240.198 Safari/537.36 OPR/72.0.3815.459",
    "Content-Type": "application/json; charset=UTF-8",
}


class Response:
    def __init__(self, request_obj: requests.Response) -> None:
        #: Integer Code of responded HTTP Status, e.g. 404 or 200.
        self.status_code = request_obj.status_code

        #: Case-insensitive Dictionary of Response Headers.
        #: For example, ``headers['content-encoding']`` will return the
        #: value of a ``'Content-Encoding'`` response header.
        self.headers = request_obj.headers

        #: File-like object representation of response (for advanced usage).
        #: Use of ``raw`` requires that ``stream=True`` be set on the request.
        #: This requirement does not apply for use internally to Requests.
        self.raw = request_obj.raw

        #: Final URL location of Response.
        self.url = request_obj.url

        #: Encoding to decode with when accessing r.text.
        self.encoding = request_obj.encoding

        #: A list of :class:`Response <Response>` objects from
        #: the history of the Request. Any redirect responses will end
        #: up here. The list is sorted from the oldest to the most recent request.
        self.history = request_obj.history

        #: Textual reason of responded HTTP Status, e.g. "Not Found" or "OK".
        self.reason = request_obj.reason

        #: A CookieJar of Cookies the server sent back.
        self.cookies = request_obj.cookies

        #: The amount of time elapsed between sending the request
        #: and the arrival of the response (as a timedelta).
        #: This property specifically measures the time taken between sending
        #: the first byte of the request and finishing parsing the headers. It
        #: is therefore unaffected by consuming the response content or the
        #: value of the ``stream`` keyword argument.
        self.elapsed = request_obj.elapsed

        #: The :class:`PreparedRequest <PreparedRequest>` object to which this
        #: is a response.
        self.request = request_obj.request

        # properties
        self.content = request_obj.content
        self.apparent_encoding = request_obj.apparent_encoding
        self.is_redirect = request_obj.is_redirect
        self.is_permanent_redirect = request_obj.is_permanent_redirect
        self.links = request_obj.links
        self.next = request_obj.next
        self.ok = request_obj.ok

    @property
    def text(self, encoding="utf-8") -> str:
        """Returns the text/str version of the response (decoded)"""
        try:
            return self.content.decode(encoding)
        except Exception:
            return str(self.content).encode(encoding).decode(encoding)

    def raise_for_status(self):
        """Raise an exception if the status code of the response is less than 400"""
        if self.status_code >= 400:
            raise RequestStatusError(
                self.status_code,
                "Request Status Code: {code}".format(code=str(self.status_code)),
            )

    def json(self, **kwargs):
        return json.loads(self.text, **kwargs)

    def as_object(self):
        return dict2object(self.json())


class Request:
    """
    Вспомогательный класс, для работы с POST и GET запросами.
    Args:
        base_url: корневой адресс сайта
        proxy_dict: словарь прокси серверов
        timeout: устанавливает таймаут на запросы
        request_retries: количество попыток после неудачного соединения
        ssl_verify: позволяет верифицировать SSL-сертификаты
    """

    def __init__(
        self,
        base_url: str,
        proxy_dict: dict = {},
        timeout: float = 10.0,
        max_retries: int = 3,
        ssl_verify: bool = False,
    ):
        self.base_url = base_url
        self.proxies = proxy_dict
        self.timeout = timeout
        self.verify = ssl_verify

        adapter = HTTPAdapter(
            pool_connections=100, pool_maxsize=100, max_retries=max_retries
        )

        self.session = requests.Session()
        self.session.headers.update(HEADER)
        self.session.mount(base_url, adapter)

    def request(self, method, url, data, *args, **kwargs) -> Response:
        try:
            response = self.session.request(
                method,
                url=f"{self.base_url}{url}",
                json=data,
                timeout=self.timeout,
                proxies=self.proxies,
                verify=self.verify,
                *args,
                **kwargs,
            )
            response.encoding = "utf-8"
        except requests.Timeout:
            raise exceptions.TimedOut()
        except (requests.RequestException, requests.exceptions.ConnectionError) as e:
            raise exceptions.NetworkError(e)
        else:
            logger.debug(
                f"URL: {self.base_url}{url}, status code: {response.status_code}, {method} request"
            )

            self.raise_by_status_code(response.status_code)

            return Response(response)

    def raise_by_status_code(self, status_code):
        # Ported from Android
        if status_code == 401:
            raise exceptions.LoginSessionExpired(
                "Сессия истекла, возобновите сессию с помощью метода login"
            )
        elif status_code == 404:
            raise exceptions.ServerError(
                f"Серверная ошибка, попробуйте чуть позже, код ошибки: {status_code}"
            )
        elif status_code >= 402:
            if status_code <= 500:
                raise exceptions.ServerError(
                    f"Серверная ошибка, попробуйте чуть позже, код ошибки: {status_code}"
                )

    def post(self, url, data=None, *args, **kwargs) -> Response:
        logger.debug(f"URL: {url}, POST request")
        response = self.request("POST", url, data, *args, **kwargs)
        return response

    def get(self, url, data=None, *args, **kwargs) -> Response:
        logger.debug(f"URL: {url}, GET request")
        response = self.request("GET", url, data, *args, **kwargs)
        return response

    @property
    def header(self):
        return self.session.header

    @header.setter
    def header(self, header_value):
        for key, value in header_value.items():
            if value is None:
                self.session.headers.pop(key)
            else:
                self.session.headers.update(header_value)

    def __dell__(self):
        self.session.close()


__all__ = ["Request"]
