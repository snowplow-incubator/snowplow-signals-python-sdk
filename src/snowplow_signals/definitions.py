from .models import Entity

# Predefined entities
user_entity = Entity(
    name="user",
    key="domain_userid",
)
session_entity = Entity(
    name="session",
    key="domain_sessionid",
)
entities: list[Entity] = [user_entity, session_entity]
