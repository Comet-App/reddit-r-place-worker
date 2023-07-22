import pickle
import time
from classes import FakeMailBox, FakePerson, Reddit
from datetime import datetime
from models import User, AccessToken
from utils import get_logger, launch_tor, TOR_PROXY
import os

logger = get_logger(__name__)
USERS_COUNT = 2  # 100000
DBC_USERNAME = os.environ.get("DBC_USERNAME")
DBC_PASSWORD = os.environ.get("DBC_PASSWORD")

logger.info("Launching tor setup")

tor_process = None

created_user_count = 0
while created_user_count < USERS_COUNT:
    logger.info(f"Creating user #{created_user_count+1}")
    person = FakePerson()
    mailbox = FakeMailBox(person)
    # Attach mailbox to user
    person.mailbox = mailbox

    if tor_process:
        tor_process.kill()
    tor_process = launch_tor()

    reddit_bot = Reddit(
        person,
        dbc_username=DBC_USERNAME,
        dbc_password=DBC_PASSWORD,
        headless=True,
        proxies=TOR_PROXY,
        logger=logger,
    )
    res = reddit_bot.create_account()

    if res:
        logger.info(f"Adding user {person.username} to database")
        user = User(
            username=person.username,
            password=person.password,
            create_account=datetime.now(),
            disabled=None,
        )
        user.save()
        try:
            logger.info(f"Generating token for user {person.username}")
            # Generate token
            token = reddit_bot.get_access_token()

            user.last_used = datetime.now()

            # Create new access token
            access_token_obj = AccessToken(
                username=user.username,
                token=token,
                created_at=datetime.now(),
            )
            access_token_obj.save()
        except Exception as e:
            logger.error(f"Failed to generate token for user {person.username}")
        created_user_count += 1

    reddit_bot.close_me()
