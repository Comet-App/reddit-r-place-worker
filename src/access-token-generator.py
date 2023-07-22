import os
from datetime import datetime
import time
from classes import Reddit, FakePerson
from models import User, AccessToken
from utils import get_logger

TIME_TO_WAIT_BETWEEN_CYCLE_IN_SECS = 60

logger = get_logger("AccessTokenGenerator")
logger.info("Starting bot cycle")

while True:
    all_users = User.select().where(User.disabled == None)  # Or disabled == False

    logger.debug(f"Found {len(all_users)} enabled users")
    for user in all_users:
        access_tokens = AccessToken.select().where(
            AccessToken.username == user.username, AccessToken.expired == False
        )
        if len(access_tokens) > 0:
            logger.debug(
                f"Skipping user {user.username} as access token already exists"
            )
            continue
        logger.debug(f"Creating new access token for {user.username}")

        fake_person = FakePerson()
        fake_person.username = user.username
        fake_person.password = user.password
        fake_person.has_reddit = True
        try:
            reddit_account = Reddit(fake_person, headless=False)
            token = reddit_account.get_access_token()
            reddit_account.close_me()
            user.last_used = datetime.now()
            user.save()

            # Create new access token
            access_token_obj = AccessToken(
                username=user.username,
                token=token,
                created_at=datetime.now(),
            )
            access_token_obj.save()
        except Exception as e:
            logger.error(
                f"Failed to generating access token for {user.username}. Error: {e}"
            )
        time.sleep(5)  # Give rest to chrome
    logger.debug(f"Sleeping for {TIME_TO_WAIT_BETWEEN_CYCLE_IN_SECS} seconds")
    time.sleep(TIME_TO_WAIT_BETWEEN_CYCLE_IN_SECS)
