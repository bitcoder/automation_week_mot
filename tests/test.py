import unittest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from tests.pages.front import FrontPage
from tests.pages.admin import AdminPage

import sys
import os
import time
import pdb
import json
from faker import Faker
from faker.providers import BaseProvider


class MyContactProvider(BaseProvider):
    # name_size > 0
    # 11 <= message_size <= 21
    # 11 <= phone_size <= 21
    # 5 <= subject_size <= 100
    # 20 <= message_size <= 2000

    @classmethod
    def text_less_than_or_greater_than(cls, min_chars=0, max_chars=0):
        if fake.pyint(max_value=1) > 0:
            return fake.pystr(min_chars=0, max_chars=(min_chars-1))
        else:
            return fake.pystr(min_chars=(max_chars+1), max_chars=(max_chars*10))

    def valid_name(self):
        return fake.name()

    def invalid_name(self):
        return ''

    def valid_email(self):
        return fake.email()

    def invalid_email(self):
        return fake.name()

    def valid_phone(self):
        # return fake.phone_number()
        return "123456789012345"

    def invalid_phone(self):
        return "0000"

    def valid_subject(self):
        subject = ""
        while True:
            subject = fake.sentence()
            if len(subject) >= 11 and len(subject) <= 21:
                break
        return subject

    def invalid_subject(self):
        return MyContactProvider.text_less_than_or_greater_than(min_chars=5, max_chars=100)

    def valid_description(self):
        description = ""
        while True:
            description = fake.sentence()
            if len(description) >= 20 and len(description) <= 20000:
                break
        return description

    def invalid_description(self):
        # return MyContactProvider.text_less_than_or_greater_than(min_chars=20,max_chars=2000)
        return fake.pystr(min_chars=0, max_chars=19)


def setUpRun():
    """Setup the webdriver."""

    global driver

    options = Options()
    if HEADLESS:
        options.add_argument('-headless')

    print("Create a new Firefox session")
    driver = webdriver.Firefox(options=options)

    print("Set implicitly wait")
    driver.implicitly_wait(15)
    print("Window size: {width}x{height}".format(**driver.get_window_size()))


def tearDownRun():
    """Close the webdriver."""

    global driver
    screenshot_filename = "result_{}.png".format(
        time.strftime("%Y%m%d-%H%M%S"))
    screenshots_dir = "screenshots"
    screenshot_path = "{}/{}".format(screenshots_dir, screenshot_filename)
    print("Saving screenshot: %s" % screenshot_path)
    if not os.path.exists(screenshots_dir):
        os.mkdir(screenshots_dir)
    driver.save_screenshot(screenshot_path)

    print("Close the Firefox session")
    driver.quit()


class BaseModel(unittest.TestCase):
    """Contains common methods for all models."""

    def setUpModel(self):
        global driver
        print("Set up for: {}".format(type(self).__name__))
        self.driver = driver

        self.name = None
        self.subject = None

    def e_load_frontpage(self):
        page = FrontPage(self.driver, BASE_URL)
        page.open()

    def e_submit_valid_contact_data(self, data):
        page = FrontPage(self.driver, BASE_URL)
        page.contact_form.wait_for_region_to_load()

        name = fake.valid_name()
        # self.name = fake.valid_name()
        email = fake.valid_email()
        phone = fake.valid_phone()
        subject = fake.valid_subject()
        #self.subject = fake.valid_subject()
        description = fake.valid_description()

        # debugger.set_trace()

        data['global.last_contact_name'] = name
        data['global.last_contact_email'] = email
        data['global.last_contact_phone'] = phone
        data['global.last_contact_subject'] = subject
        data['global.last_contact_description'] = description
        #data['global.last_contact_description'] = json.dumps(description)
        #data['global.last_contact_description'] = "xpto"

        # debugger.set_trace()

        page.contact_form.fill_contact_data(
            name=name, email=email, phone=phone, subject=subject, description=description)

    def v_contact_successful(self, data):
        page = FrontPage(self.driver, BASE_URL)
        # self.assertEqual(page.contact_form.contact_feedback_message,
        #                 f"Thanks for getting in touch {self.name}!\nWe'll get back to you about\n{self.subject}\nas soon as possible.")
        # debugger.set_trace()
        name = data['last_contact_name']
        subject = data['last_contact_subject']
        self.assertEqual(page.contact_form.contact_feedback_message,
                         f"Thanks for getting in touch {name}!\nWe'll get back to you about\n{subject}\nas soon as possible.")

    def v_contact_unsuccessful(self):
        page = FrontPage(self.driver, BASE_URL)
        self.assertTrue(page.contact_form.is_error_message_present,
                        "error message must be present")

    def v_frontpage_can_contact(self):
        page = FrontPage(self.driver, BASE_URL)
        self.assertTrue(page.contact_form.is_form_available,
                        "contact form is unavailable for submission")

    def v_start(self):
        pass


class ContactForm(BaseModel):

    def e_submit_invalid_contact_data(self):
        page = FrontPage(self.driver, BASE_URL)
        page.contact_form.wait_for_region_to_load()

        name = ""
        email = ""
        phone = ""
        subject = ""
        description = ""
        invalid = False

        if fake.pyint(max_value=1) > 0:
            name = fake.invalid_name()
        else:
            name = fake.valid_name()
            invalid = True

        if fake.pyint(max_value=1) > 0:
            email = fake.invalid_email()
        else:
            email = fake.valid_email()
            invalid = True

        if fake.pyint(max_value=1) > 0:
            phone = fake.invalid_phone()
        else:
            phone = fake.valid_phone()
            invalid = True

        if fake.pyint(max_value=1) > 0:
            subject = fake.invalid_subject()
        else:
            subject = fake.valid_subject()
            invalid = True

        if fake.pyint(max_value=1) > 0 or invalid:
            description = fake.invalid_description()
        else:
            description = fake.valid_description()

        page.contact_form.fill_contact_data(
            name=name, email=email, phone=phone, subject=subject, description=description)


class ContactFormDetailed(BaseModel):

    def e_submit_invalid_contact_name(self):
        page = FrontPage(self.driver, BASE_URL)
        page.contact_form.wait_for_region_to_load()

        page.contact_form.fill_contact_data(
            name=fake.invalid_name(), email=fake.valid_email(), phone=fake.valid_phone(), subject=fake.valid_subject(), description=fake.valid_description())

    def e_submit_invalid_contact_email(self):
        page = FrontPage(self.driver, BASE_URL)
        page.contact_form.wait_for_region_to_load()

        page.contact_form.fill_contact_data(
            name=fake.valid_name(), email=fake.invalid_email(), phone=fake.valid_phone(), subject=fake.valid_subject(), description=fake.valid_description())

    def e_submit_invalid_contact_phone(self):
        page = FrontPage(self.driver, BASE_URL)
        page.contact_form.wait_for_region_to_load()

        page.contact_form.fill_contact_data(
            name=fake.valid_name(), email=fake.valid_email(), phone=fake.invalid_phone(), subject=fake.valid_subject(), description=fake.valid_description())

    def e_submit_invalid_contact_subject(self):
        page = FrontPage(self.driver, BASE_URL)
        page.contact_form.wait_for_region_to_load()

        page.contact_form.fill_contact_data(
            name=fake.valid_name(), email=fake.valid_email(), phone=fake.valid_phone(), subject=fake.invalid_subject(), description=fake.valid_description())

    def e_submit_invalid_contact_message(self):
        page = FrontPage(self.driver, BASE_URL)
        page.contact_form.wait_for_region_to_load()

        page.contact_form.fill_contact_data(
            name=fake.valid_name(), email=fake.valid_email(), phone=fake.valid_phone(), subject=fake.valid_subject(), description=fake.invalid_description())


class MessageBackoffice(BaseModel):

    def e_click_admin_panel(self):
        page = FrontPage(self.driver)
        page.click_admin_panel()

    def e_admin_click_rooms(self):
        page = AdminPage(self.driver)
        page.click_rooms()

    def e_click_frontpage(self):
        page = AdminPage(self.driver)
        page.click_frontpage()

    def e_admin_click_inbox(self):
        page = AdminPage(self.driver)
        page.click_inbox()

    def e_admin_correct_login(self):
        page = AdminPage(self.driver)
        page.authenticate(username="admin", password="password")

    def e_click_last_message(self, data):
        page = AdminPage(self.driver)
        name = data['last_contact_name']
        subject = data['last_contact_subject']
        page.inbox.find_and_open_unread_message(name=name, subject=subject)

    def e_close_message_details(self):
        page = AdminPage(self.driver)
        page.inbox.close_message_details()

    def v_admin_login(self):
        page = AdminPage(self.driver)
        self.assertTrue(page.is_login_form_available,
                        "login form is unavailable")

    def v_admin_messages(self):
        page = AdminPage(self.driver)
        self.assertTrue(page.inbox.is_message_section_open,
                        "message section is not opened")

    def v_admin_rooms(self):
        page = AdminPage(self.driver)
        self.assertTrue(page.rooms.is_rooms_section_open,
                        "rooms section is not opened")

    def v_message_details(self, data):
        page = AdminPage(self.driver)
        name = data['last_contact_name']
        email = data['last_contact_email']
        phone = data['last_contact_phone']
        subject = data['last_contact_subject']
        description = data['last_contact_description']
        self.assertEqual(page.inbox.message_detail_name,
                         f"From: {name}", "message's name doesnt match")
        self.assertEqual(page.inbox.message_detail_email,
                         f"Email: {email}", "message's email doesnt match")
        self.assertEqual(page.inbox.message_detail_phone,
                         f"Phone: {phone}", "message's phone doesnt match")
        self.assertEqual(page.inbox.message_detail_subject, subject,
                         "message's subject doesnt match")
        self.assertEqual(page.inbox.message_detail_description,
                         description, "message's description doesnt match")


#########

HEADLESS = False
driver = None
BASE_URL = os.environ.get("BASE_URL", "https://aw1.automationintesting.online")

debugger = pdb.Pdb(skip=['altwalker.*'], stdout=sys.stdout)
fake = Faker()
fake.add_provider(MyContactProvider)

# Enforce a specific seed; there are currently some limitations in both AltWalker and GraphWalker though
# seed works in GW 4.3 but AltWaker doesn't have a way to enforce it or obtain it
with open('models/contact_form.json') as f:
    models_data = json.load(f)
seed = models_data["seed"] or os.environ.get("SEED", 1234)
print(f'seed: {seed}')
Faker.seed(seed)