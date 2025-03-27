from .attributes import add_to_cart_count_attribute
from snowplow_signals import Signals, View, Service, session_entity


def main():
    sp_signals = Signals()

    view = View(
        entity=session_entity,
        name="new_feature_views",
        version=1,
        features=[add_to_cart_count_attribute],
    )

    service = Service(name="new_fs", views=[view])

    sp_signals.apply(objects=[view, service])


if __name__ == "__main__":
    main()
