from typing import Optional
import requests
from .types.browser_features import BrowserFeatures

# BASE_URL = "http://127.0.0.1:6566"
BASE_URL = "https://a24c-2a01-c846-19c2-c800-686d-95ea-67cd-5654.ngrok-free.app"


def get_features_from_cookie(
    cookie: str, cookie_name: str = "_sp_id"
) -> BrowserFeatures:
    cookie_list = cookie.split(cookie_name)[1].split(".")
    domain_userid = cookie_list[1].split("=")[1]
    return BrowserFeatures.initialize(
        {
            "domain_userid": domain_userid,
            "domain_sessionidx": cookie_list[2],
            "domain_sessionid": cookie_list[5],
        }
    )


def make_post_request(url: str, data: Optional[dict], headers: Optional[dict]):
    url = f"{BASE_URL}/{url}"
    response = requests.post(url, json=data, headers=headers)
    return response.json()
