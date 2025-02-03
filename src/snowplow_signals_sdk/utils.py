from typing import Optional
import requests
import warnings
import json
from .models.browser_features import BrowserFeatures


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
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        warnings.warn(
            f"Error making a request to Console: {json.loads(response.text)['message']}"
        )
        return None

    return response.json()
