from snowplow_signals_sdk.utils import get_features_from_cookie


def test_get_features_from_cookie():
    features_from_cookie = get_features_from_cookie(
        cookie="_sp_id.1fff=b2f35890-edb0-449c-a77e-2b9c74955306.1738251412.2.1738264145.7bd3d340-2ac0-43d6-878e-49ac97c6611e.cb06c04f-7367-46d4-9ce5-954e57d99890.7ff7cb56-7864-4a23-92ad-7905d5fa218a.1738264145366.1"
    )
    assert (
        features_from_cookie.domain_sessionid == "7bd3d340-2ac0-43d6-878e-49ac97c6611e"
    )
    assert features_from_cookie.domain_sessionidx == "1738251412"
    assert features_from_cookie.domain_userid == "b2f35890-edb0-449c-a77e-2b9c74955306"
