import logging
import requests
from requests.adapters import HTTPAdapter

logging.basicConfig(level=logging.DEBUG)

USER_AGENT_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4240.198 Safari/537.36 OPR/72.0.3815.459'}

class RequestSessionWrapper:
    
    def __init__(self, base_platonus_url, max_request_retries=3):
        self.platonus_adapter = HTTPAdapter(max_request_retries)
        self.session = requests.Session()
        self.session.headers.update(USER_AGENT_HEADER)
        # использование `platonus_adapter` для всех запросов, которые начинаются с указанным URL
        self.session.mount(base_platonus_url, self.platonus_adapter)
    
    def request(self, *args, **kwargs):
        request = self.session.request(*args, **kwargs)
        request.encoding = 'utf-8'
        #logging.info(f"Request status code: {request.status_code}")
        return request
        
    def post(self, url, *args, **kwargs):
        result = self.request('POST', url, *args, **kwargs)
        #logging.info(f"URL: {url}, POST result contetnt: {result.json()}")
        return result
    
    def get(self, url, *args, **kwargs):
        result = self.request('GET', url, *args, **kwargs)
        #logging.info(f"URL: {url}, GET result contetnt: {result.content}")
        return result