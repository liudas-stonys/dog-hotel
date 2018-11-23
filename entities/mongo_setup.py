import mongoengine

alias_core = "core"
db = "dog_hotel"


def global_init():
    mongoengine.register_connection(alias=alias_core, name=db)
