import re
import logging
import requests
from urllib.parse import urlsplit, urlparse
from platonus_api import exception
from requests.adapters import HTTPAdapter

logging.basicConfig(level=logging.INFO)

CUSTOM_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4240.198 Safari/537.36 OPR/72.0.3815.459', 'Content-Type': 'application/json; charset=UTF-8'}


class RequestSessionWrapper:
    def __init__(self, base_url, request_retries=3):
        self.base_url = base_url
        self.base_url_adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=request_retries)
        self.session = requests.Session()
        self.session.headers.update(CUSTOM_HEADER)
        self.session.mount(base_url, self.base_url_adapter)  # использование 'base_url_adapter' для всех запросов, которые начинаются с указанным URL

    def request(self, method, url, *args, **kwargs):
        response = self.session.request(method, f"{self.base_url}{url}", *args, **kwargs, timeout=10.0)
        request_inf = f"URL: {url}, status code: {response.status_code}, {method} response contetnt: {response.content}"

        if response.status_code == 401:
            raise exception.InvalidToken("Seems login session is timeout")
        elif response.status_code == 404:
            raise exception.ServerError(request_inf)
        elif 402 <= response.status_code:
            if 500 >= response.status_code:
                raise exception.ServerError(request_inf)

        #response.raise_for_status()
        response.encoding = 'utf-8'
        #logging.info(request_inf)
        return response

    def post(self, url, *args, **kwargs):
        response = self.request('POST', url, *args, **kwargs)
        return response

    def get(self, url, *args, **kwargs):
        response = self.request('GET', url, *args, **kwargs)
        return response

    def load_session(self, session):
        self.session = session

    def save_session(self):
        return self.session


def URLValidator(url):
    # Код взят от сюда: https://github.com/django/django/blob/master/django/core/validators.py

    ul = '\u00a1-\uffff'  # Unicode letters range (must not be a raw string).

    # IP patterns
    ipv4_re = r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
    ipv6_re = r'\[[0-9a-f:.]+\]'  # (simple regex, validated later)

    # Host patterns
    hostname_re = r'[a-z' + ul + r'0-9](?:[a-z' + ul + r'0-9-]{0,61}[a-z' + ul + r'0-9])?'
    # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
    domain_re = r'(?:\.(?!-)[a-z' + ul + r'0-9-]{1,63}(?<!-))*'

    tld_re = (
        r'\.'                                # dot
        r'(?!-)'                             # can't start with a dash
        r'(?:[a-z' + ul + '-]{2,63}'         # domain label
        r'|xn--[a-z0-9]{1,59})'              # or punycode label
        r'(?<!-)'                            # can't end with a dash
        r'\.?'                               # may have a trailing dot
    )
    host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'

    regex = re.compile(
        r'^(?:[a-z0-9.+-]*)://'  # scheme is validated separately
        r'(?:[^\s:@/]+(?::[^\s:@/]*)?@)?'  # user:pass authentication
        r'(?:' + ipv4_re + '|' + ipv6_re + '|' + host_re + ')'
        r'(?::\d{2,5})?'  # port
        r'(?:[/?#][^\s]*)?'  # resource path
        r'\Z', re.IGNORECASE)

    url_check_re = re.match(regex, url) is not None

    if not url_check_re:
        raise exception.InvalidURL("Не валидный адрес сайта. Пример правильного адреса: http://www.example.com/")

    schemes = ['http', 'https']
    scheme = url.split('://')[0].lower()

    if scheme not in schemes:
        raise exception.InvalidURL(f"Протокол {scheme} не поддеживается. Поддерживаемые протоколы передачи данных: {schemes}")

    if len(urlsplit(url).hostname) > 253:
        raise exception.InvalidURL("URL адрес сайта превышает 253 символов")

def URLNormalizer(url, context):
    parsed_url = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}{context}'.format(uri=parsed_url, context=context)
    return result
