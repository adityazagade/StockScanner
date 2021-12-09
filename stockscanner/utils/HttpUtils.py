import requests
import logging

from stockscanner.utils import Constants

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'accept-language': 'en,gu;q=0.9,hi;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
}

cookies = {}


def get_Cookies():
    global cookies
    if len(cookies) == 0:
        session = requests.Session()
        dummy_response_to_get_cookies = session.get(Constants.BASE_URL, headers=headers, timeout=30)
        logger.info("Cookies are fetched")
        cookies = dict(dummy_response_to_get_cookies.cookies)
    return cookies


def do_get(url, query_parameters={}):
    response = requests.get(url, params=query_parameters, headers=headers, timeout=30, cookies=get_Cookies())
    if 200 <= response.status_code < 300:
        return response.text


def do_post():
    pass


def download_file(url, query_param={}):
    with requests.Session() as s:
        response = s.get(url, params=query_param, headers=headers, cookies=get_Cookies(), timeout=30)
    return response.content
