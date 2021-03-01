import logging
import requests
import exception
from requests.adapters import HTTPAdapter

logging.basicConfig(level=logging.INFO)

CUSTOM_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4240.198 Safari/537.36 OPR/72.0.3815.459', 'Content-Type': 'application/json; charset=UTF-8'}

class RequestSessionWrapper:
    
    def __init__(self, base_url, request_retries=3):
        self.base_url = base_url
        self.base_url_adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=request_retries)
        self.session = requests.Session()
        self.session.headers.update(CUSTOM_HEADER)
        self.session.mount(base_url, self.base_url_adapter) # использование 'base_url_adapter' для всех запросов, которые начинаются с указанным URL
    
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
