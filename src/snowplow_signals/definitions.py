from .models import AttributeKey, Event

# Predefined attribute keys
user_attribute_key = AttributeKey(
    name="user",
    key="domain_userid",
    description="Deprecated: Use domain_userid instead.",
)
session_attribute_key = AttributeKey(
    name="session",
    key="domain_sessionid",
    description="Deprecated: Use domain_sessionid instead.",
)

domain_userid = AttributeKey(
    name="domain_userid",
    key="domain_userid",
    description="The domain user ID for the user.",
)
domain_sessionid = AttributeKey(
    name="domain_sessionid",
    key="domain_sessionid",
    description="The domain session ID for the session.",
)

user_id = AttributeKey(
    name="user_id",
    key="user_id",
    description="The user ID for the user.",
)

network_userid = AttributeKey(
    name="network_userid",
    key="network_userid",
    description="The network user ID for the user.",
)


def PageView():
    return Event(
        vendor="com.snowplowanalytics.snowplow",
        name="page_view",
        version="1-0-0",
    )


def PagePing():
    return Event(
        vendor="com.snowplowanalytics.snowplow",
        name="page_ping",
        version="1-0-0",
    )


def StructuredEvent():
    return Event(name="event", vendor="com.google.analytics", version="1-0-0")
