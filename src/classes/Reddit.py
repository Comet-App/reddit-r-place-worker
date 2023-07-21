from .FakePerson import FakePerson
import re
import json
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from deathbycaptcha import deathbycaptcha
from random import randint, sample
from bs4 import BeautifulSoup

import time
from utils import get_logger

MAX_INTERESTS_TO_SELECT = 7
BROWSER_WINDOW_WIDTH = 1360
BROWSER_WINDOW_HEIGHT = 768
GOOGLE_RECAPTCHA_URL_PATTERN = "google.com/recaptcha/api"
HCAPTCHA_URL_PATTERN = "hcaptcha.com/captcha/v1"
REDDIT_RECAPTCHA_SITE_KEY = "6LeTnxkTAAAAAN9QEuDZRpn90WwKk_R1TRW_g-JC"


class Reddit:
    REGISTER_URL = "https://www.reddit.com/register/"

    def __init__(
        self,
        person: FakePerson,
        headless=True,
        dbc_username=None,
        dbc_password=None,
        logger=None,
    ):
        self.person = person
        self.logger = logger or get_logger(__name__)

        # Init selenium driver
        self.driver = uc.Chrome(headless=headless, use_subprocess=False)
        self.driver.set_window_size(BROWSER_WINDOW_WIDTH, BROWSER_WINDOW_HEIGHT)

        # Death by captcha setup
        if dbc_username is None or dbc_password is None:
            self.logger.critical("Death by captcha username and password not provided")
            raise Exception("Death by captcha username or password not provided")

        self.dbc_client = deathbycaptcha.HttpClient(dbc_username, dbc_password)
        self.check_deathbycaptcha_balance()

    def check_deathbycaptcha_balance(self):
        try:
            balance = self.dbc_client.get_balance()
            if balance == 0:
                self.logger.error("No balance left in account")
                raise Exception("No balance left in account")
        except deathbycaptcha.AccessDeniedException:
            # Access to DBC API denied, check your credentials and/or balance
            raise Exception(
                "error: Access to DBC API denied,"
                + "check your credentials and/or balance"
            )

    def get_recaptcha_cookie_token(self):
        # Put the proxy and reCaptcha token data
        captcha_dict = {
            "proxy": "",
            "proxytype": "",
            "googlekey": REDDIT_RECAPTCHA_SITE_KEY,
            "pageurl": self.driver.current_url,
        }

        # Create a json string
        json_captcha = json.dumps(captcha_dict)
        tokenContainer = ""

        self.check_deathbycaptcha_balance()

        try:
            # Put your CAPTCHA type and Json payload here:
            captcha = self.dbc_client.decode(type=4, token_params=json_captcha)
            assert (
                captcha is not None
            ), "Captcha didn't solve correctly by deathbycaptcha"
            # The CAPTCHA was solved; captcha["captcha"] item holds its
            # numeric ID, and captcha["text"] item its list of "coordinates".
            # print("CAPTCHA %s solved: %s" % (captcha["captcha"], captcha["text"]))
            tokenContainer = captcha["text"]
            if captcha["text"] == "":  # check if the CAPTCHA was incorrectly solved
                self.dbc_client.report(captcha["captcha"])
                raise Exception("Captcha not solved correctly")
        except deathbycaptcha.AccessDeniedException:
            # Access to DBC API denied, check your credentials and/or balance
            raise Exception(
                "error: Access to DBC API denied,"
                + "check your credentials and/or balance"
            )

        return tokenContainer

    def solve_google_recaptcha(self):
        token = self.get_recaptcha_cookie_token()
        self.driver.execute_script(
            f"document.getElementById('g-recaptcha-response').innerHTML='{token}'"
        )
        # Set some sleep as in the docs
        time.sleep(2)
        self.logger.debug("Recaptcha is resolved successfully")
        return True

    def is_google_recaptcha(self):
        iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe")
        for iframe in iframes:
            iframe_src = iframe.get_attribute("src")
            if GOOGLE_RECAPTCHA_URL_PATTERN in iframe_src:
                # Check if we have already solved the captcha or not
                return True
        return False

    def sleep_randomly(self, min_time: int = 1, max_time: int = 5):
        if max_time < min_time:
            max_time = min_time + 5
        sleep_time = randint(min_time, max_time)
        self.logger.debug(f"Sleeping for {sleep_time} seconds")
        time.sleep(sleep_time)

    def is_duplicate_username(self):
        error_message_elements = self.driver.find_elements(
            By.CLASS_NAME, "AnimatedForm__errorMessage"
        )

        for error_message_element in error_message_elements:
            if error_message_element.text == "That username is already taken":
                return True
        return False

    def check_for_submit_rate_limit(self):
        submit_status_element = None
        try:
            submit_status_element = self.driver.find_element(
                By.CSS_SELECTOR,
                "div.AnimatedForm__bottomNav > span > span.AnimatedForm__submitStatusMessage",
            )
        except Exception as e:
            return False
        if submit_status_element:
            if "Looks like you've been doing that a lot" in submit_status_element.text:
                return True

        return False

    def select_gender_for_user(self):
        person_sex = self.person.sex
        if person_sex == "F":
            gender_element = self.driver.find_element(
                By.CSS_SELECTOR, "input[value=FEMALE]"
            )
        else:
            # Find male
            gender_element = self.driver.find_element(
                By.CSS_SELECTOR, "input[value=MALE]"
            )

        gender_element.click()
        self.sleep_randomly(1, 4)
        # No need to press continue here

    def find_and_click_continue_button(self):
        try:
            # Find first button which contains 'Continue'
            continue_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Continue')]"
            )
            continue_button.click()
            self.sleep_randomly(2, 4)
        except Exception as e:
            self.logger.error(e)
        return None

    def select_random_interests_for_user(self, max_interests=MAX_INTERESTS_TO_SELECT):
        interests_buttons_elements = self.driver.find_elements(
            By.XPATH,
            '//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[4]/div/div/div/div[1]/div/button',
        )
        assert (
            len(interests_buttons_elements) > max_interests
        ), "Interests buttons are less than max_interests"
        selected_button_elements = sample(interests_buttons_elements, max_interests)

        selected_interests = []
        for interest_button_element in selected_button_elements:
            selected_interests.append(
                interest_button_element.text or interest_button_element.accessible_name
            )
            # Scroll up/down to the button to pull it into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", interest_button_element
            )
            interest_button_element.click()
            self.sleep_randomly(1, 2)

        self.find_and_click_continue_button()

        self.person.interests = selected_interests

    def select_all_given_subreddits(self):
        subreddit_join_buttons = self.driver.find_elements(
            By.XPATH, "//button[contains(text(), 'Select All')]"
        )

        for button in subreddit_join_buttons:
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()
            self.sleep_randomly(1, 2)

        self.find_and_click_continue_button()

    def continue_with_language(self):
        # TODO: Maybe do something for language selection later
        self.find_and_click_continue_button()
        self.sleep_randomly(4, 8)

    def get_email_verification_link(self, max_retries=10):
        try_count = 0
        while try_count < max_retries:
            try_count += 1
            self.sleep_randomly(10, 20)
            messages = self.person.mailbox.get_messages()
            if len(messages) > 0:
                for message in messages:
                    if message.subject == "Verify your Reddit email address":
                        soup = BeautifulSoup(message.html_body, "lxml")

                        anchors = soup.find_all("a")
                        for anchor in anchors:
                            if anchor.text == "Verify Email Address":
                                return anchor.attrs["href"]
        return None

    def create_account(self) -> bool:
        self.logger.info(f"Creating account with username: {self.person.username}")
        self.logger.debug("Going to reddit homepage")
        self.driver.get(self.REGISTER_URL)
        self.sleep_randomly()

        self.logger.debug("Entering email details")
        self.driver.find_element(By.ID, "regEmail").send_keys(self.person.email)
        self.sleep_randomly()

        self.logger.debug("Submitting email step")
        email_submit_button = self.driver.find_element(
            By.CSS_SELECTOR,
            "div.Step__content > form > fieldset.AnimatedForm__field.m-small-margin > button",
        )
        email_submit_button.click()
        self.sleep_randomly()

        while True:
            self.logger.debug("Entering in username...")
            self.driver.find_element(By.ID, "regUsername").click()
            self.driver.find_element(By.ID, "regUsername").clear()
            self.driver.find_element(By.ID, "regUsername").send_keys(
                self.person.username
            )
            self.sleep_randomly()

            if not self.is_duplicate_username():
                break
            self.person.username = self.person.username + str(randint(0, 9))
            self.logger.debug(
                f"Username is duplicate. Trying again with {self.person.username}"
            )

        self.logger.debug("Entering in password...")
        self.driver.find_element(By.ID, "regPassword").send_keys(self.person.password)
        self.sleep_randomly(5, 10)

        # Solve captcha
        if self.is_google_recaptcha():
            self.logger.debug("Google recaptcha detected")
            try:
                response = self.solve_google_recaptcha()
                if response:
                    self.logger.info(
                        f"Google recaptcha solved successfully using death by captcha"
                    )
                else:
                    self.logger.error(
                        "Google recaptcha failed to solve, going to use regular method"
                    )
            except Exception as e:
                self.logger.error(e)

        self.logger.debug("Submitting form")
        self.driver.find_element(
            By.CSS_SELECTOR, "div.AnimatedForm__bottomNav > button"
        ).click()
        self.sleep_randomly(1, 5)

        if self.check_for_submit_rate_limit():
            self.logger.critical("Rate limit reached for the current IP")
            self.driver.close()
            # It expires session so need to do the whole thing again
            return False

        # Wait for page redirection and pop-up for gender selection
        self.sleep_randomly(10, 20)
        self.select_gender_for_user()
        self.select_random_interests_for_user()
        self.select_all_given_subreddits()
        self.continue_with_language()
        # Continue button for the avataar
        self.find_and_click_continue_button()
        self.sleep_randomly(8, 15)

        # Email confirmation
        self.logger.info("Checking email for verification message")
        email_verification_link = self.get_email_verification_link()

        assert email_verification_link is not None, "Email verification link not found"

        self.logger.debug("Going to verification link...")

        self.driver.get(email_verification_link)
        self.sleep_randomly()

        self.logger.info("Successfully created account!")
        self.driver.close()
        return True
