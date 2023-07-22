from .database import BaseModel
from peewee import CharField, BooleanField, TextField, DateTimeField


class User(BaseModel):
    class Meta:
        table_name = "users"

    username = CharField()
    created_at = DateTimeField()
    username = CharField()
    password = TextField()
    last_used = DateTimeField()
    disabled = BooleanField(default=False)
