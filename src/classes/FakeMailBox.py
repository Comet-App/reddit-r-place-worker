from onesecmail import OneSecMail
from random import choice
from .FakePerson import FakePerson


class FakeMailBox:
    def __init__(self, person: FakePerson):
        super().__init__()
        self.person = person
        self.generate_email_address()

    @property
    def available_domains(self):
        return self._get_available_domains()

    def _get_available_domains(self):
        return OneSecMail.get_available_domains()

    def _get_random_domain(self):
        return choice(self.available_domains)

    def generate_email_address(self, email_address=None):
        if email_address is None:
            email_address = f"{self.person.username}@{self._get_random_domain()}"
        self.email_address = email_address
        self.person.set_email(self.email_address)
        self.generate_emailbox()

    def generate_emailbox(self):
        self.email_inbox = OneSecMail.from_address(self.email_address)

    def get_messages(self):
        return self.email_inbox.get_messages()
