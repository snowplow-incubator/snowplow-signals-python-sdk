import json
import warnings
from typing import Optional

import requests

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
