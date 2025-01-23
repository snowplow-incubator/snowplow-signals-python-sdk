from snowplow_signals_python_sdk.signals.signals_ai import SignalsAI


def main():
    sp_signals = SignalsAI()
    features_from_cookie = sp_signals.get_features_from_cookie(
        cookie='{"session_count": 7, "latest_list_view":"product_a", "last_visited_page": "acme.com/about"}'
    )
    last_visited_page = features_from_cookie.get("last_visited_page")
    print(f"The last page the visitor visited was {last_visited_page}")


if __name__ == "__main__":
    main()
