import datetime
import mongoengine


class Owner(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    name = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)
    is_host = mongoengine.BooleanField(required=True)

    dog_ids = mongoengine.ListField()
    room_ids = mongoengine.ListField()

    meta = {
        "db_alias": "core",
        "collection": "owners"
    }
