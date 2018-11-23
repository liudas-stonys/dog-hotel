import datetime
import mongoengine


class Dog(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    breed = mongoengine.StringField(required=True)

    weight = mongoengine.FloatField(required=True)
    name = mongoengine.StringField(required=True)
    is_aggressive = mongoengine.BooleanField(required=True)

    meta = {
        "db_alias": "core",
        "collection": "dogs"
    }
