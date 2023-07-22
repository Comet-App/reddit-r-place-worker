from .database import BaseModel
from peewee import CharField, BooleanField, TextField, DateTimeField


class AccessToken(BaseModel):
    class Meta:
        table_name = "access_tokens"

    username = CharField()
    created_at = DateTimeField()
    last_used = DateTimeField()
    token = TextField()
    expired = BooleanField(default=False)
