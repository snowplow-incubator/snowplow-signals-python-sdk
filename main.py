from snowplow_signals_python_sdk.signals_ai.signals_ai import SignalsAI
from snowplow_signals_python_sdk.features.feature_service import FeatureService
from snowplow_signals_python_sdk.utils.utils import get_features_from_cookie



def main():
    browser_features = get_features_from_cookie(
        cookie="_sp_id.1fff=b2f35890-edb0-449c-a77e-2b9c74955306.1738251412.2.1738264145.1738255199.7bd3d340-2ac0-43d6-878e-49ac97c6611e.cb06c04f-7367-46d4-9ce5-954e57d99890.7ff7cb56-7864-4a23-92ad-7905d5fa218a.1738264145366.1"
    )
    sp_signals = SignalsAI(browser_features=browser_features)
    feature_service = FeatureService(name="user_features")

    online_features_df = sp_signals.get_online_features(
        features=feature_service, entity_type_id="domain_userid"
    ).to_dataframe()
    print(online_features_df)


if __name__ == "__main__":
    main()
