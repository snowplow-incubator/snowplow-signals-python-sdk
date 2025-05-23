from .models import Entity

# Predefined entities
user_entity = Entity(
    name="user",
    key="domain_userid",
    description="Deprecated: Use domain_userid instead.",
)
session_entity = Entity(
    name="session",
    key="domain_sessionid",
    description="Deprecated: Use domain_sessionid instead.",
)

domain_userid = Entity(
    name="domain_userid",
    key="domain_userid",
    description="The domain user ID for the user.",
)
domain_sessionid = Entity(
    name="domain_sessionid",
    key="domain_sessionid",
    description="The domain session ID for the session.",
)

user_id = Entity(
    name="user_id",
    key="user_id",
    description="The user ID for the user.",
)

network_userid = Entity(
    name="network_userid",
    key="network_userid",
    description="The network user ID for the user.",
)
