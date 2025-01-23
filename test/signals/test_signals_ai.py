from snowplow_signals_python_sdk.signals.signals_ai import SignalsAI


def test_get_features_from_cookie():
    sp_signals = SignalsAI()

    features_from_cookie = sp_signals.get_features_from_cookie(
        cookie='{"session_count": 7, "latest_list_view":"product_a", "last_visited_page": "acme.com/about"}'
    )
    session_count = features_from_cookie.get("session_count")
    latest_list_view = features_from_cookie.get("latest_list_view")
    last_visited_page = features_from_cookie.get("last_visited_page")
    assert session_count == 7
    assert latest_list_view == "product_a"
    assert last_visited_page == "acme.com/about"
