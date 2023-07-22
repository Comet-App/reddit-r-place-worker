import pickle
from classes import FakeMailBox, FakePerson, Reddit
from utils import get_logger
import os

logger = get_logger(__name__)
USERS_COUNT = 1  # 100000
DBC_USERNAME = os.getenv("DBC_USERNAME")
DBC_PASSWORD = os.getenv("DBC_PASSWORD")

created_user_count = 0
while created_user_count < USERS_COUNT:
    logger.info(f"Creating user #{created_user_count+1}")
    person = FakePerson()
    mailbox = FakeMailBox(person)
    # Attach mailbox to user
    person.mailbox = mailbox

    reddit_bot = Reddit(
        person, dbc_username=DBC_USERNAME, dbc_password=DBC_PASSWORD, headless=True
    )
    res = reddit_bot.create_account()

    if res:
        with open(f"user-{person.username}", "wb") as f:
            pickle.dump(person, f)
        created_user_count += 1
    # Find a way to store this user globally
