import secrets
import string
from random import choice
from faker import Faker
import reverse_geocoder as rg
from random import randint

COUNTRY_LIST = ["it_IT", "en_US", "ja_JP"]


class FakePerson:
    __FIELDS_TO_AVOID = [
        "ssn",
        "residence",
        "blood_group",
        "website",
        "company",
        "mail",
        "current_location",
    ]

    def __init__(self, country=None, seed=0):
        if country is None:
            self.country = choice(COUNTRY_LIST)
        else:
            assert country in COUNTRY_LIST
            self.country = country
        # Custom faker
        # TODO: Use a way to pass seed
        self.__fake = Faker([self.country])
        profile = self.__fake.profile()
        for key in profile:
            if key not in self.__FIELDS_TO_AVOID:
                setattr(self, key, profile[key])

        location_dict = FakePerson.city_state_country(
            profile["current_location"][0], profile["current_location"][1]
        )

        self.password_length = randint(8, 16)
        self.generate_password()
        self.city = location_dict["city"]
        self.state = location_dict["state"]
        self.country = location_dict["country"]
        self.color = self.__fake.color_name()
        self.interests = []

    @staticmethod
    def city_state_country(latitude, longitude):
        results = rg.search((latitude, longitude), mode=1)
        if len(results) == 0:
            return {"city": "", "state": "", "country": ""}

        city = results[0]["name"]
        country = results[0]["cc"]
        state = results[0]["admin1"]
        return {"city": city, "state": state, "country": country}

    def set_email(self, email: str):
        self.email = email

    def generate_password(self):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        alphabet = string.ascii_letters + string.digits
        self.password = "".join(
            secrets.choice(alphabet) for i in range(self.password_length)
        )
