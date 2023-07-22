from peewee import *
import os

DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")

database = PostgresqlDatabase(
    DB_NAME, user=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST, port=5432
)


class BaseModel(Model):
    """A base model that will use our Postgresql database"""

    class Meta:
        database = database
