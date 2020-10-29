import unittest
import pytest

from tests.pages.front import FrontPage
from tests.pages.admin import AdminPage

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options

import os
import pdb
import sys
import time
from datetime import date, datetime, timedelta
from faker import Faker
from configparser import ConfigParser
from faker.providers import BaseProvider
from tests.my_contact_provider import MyContactProvider
from tests.booker_api import BookerAPI

class ContactFormTestCase(unittest.TestCase):

    def setUp(self):
        options = Options()
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(15)
        self.driver.maximize_window()

        self.booker_api = BookerAPI(base_url=BASE_URL,
                                    username=BOOKER_API_USERNAME, password=BOOKER_API_PASSWORD)

    def tearDown(self):
        self.driver.quit()

    @pytest.mark.ch1
    def test_contact_form_successful(self):
        page = FrontPage(self.driver, BASE_URL)
        page.open()
        page.contact_form.wait_for_region_to_load()

        name = fake.valid_name()
        email = fake.valid_email()
        phone = fake.valid_phone()
        subject = fake.valid_subject()
        description = fake.valid_description()

        page.contact_form.fill_contact_data(
            name=name, email=email, phone=phone, subject=subject, description=description)
        self.assertEqual(page.contact_form.contact_feedback_message,
                         f"Thanks for getting in touch {name}!\nWe'll get back to you about\n{subject}\nas soon as possible.")

    @pytest.mark.ch1n
    def test_contact_form_unsuccessfail_invalid_name(self):
        page = FrontPage(self.driver, BASE_URL)
        page.open()
        page.contact_form.wait_for_region_to_load()

        name = fake.invalid_name()
        email = fake.valid_email()
        phone = fake.valid_phone()
        subject = fake.valid_subject()
        description = fake.valid_description()

        page.contact_form.fill_contact_data(
            name=name, email=email, phone=phone, subject=subject, description=description)
        self.assertTrue(page.contact_form.is_error_message_present,
                        "error message must be present")

    @pytest.mark.ch2
    def test_contact_message_received_in_backoffice(self):
        page = FrontPage(self.driver, BASE_URL)
        page.open()
        page.contact_form.wait_for_region_to_load()

        name = fake.valid_name()
        email = fake.valid_email()
        phone = fake.valid_phone()
        subject = fake.valid_subject()
        description = fake.valid_description()

        page.contact_form.fill_contact_data(
            name=name, email=email, phone=phone, subject=subject, description=description)
        page.click_admin_panel()
        page = AdminPage(self.driver)
        page.authenticate_with_valid_credentials()
        self.assertTrue(page.rooms.is_rooms_section_open,
                        "rooms section is not opened")
        page.click_inbox()
        self.assertTrue(page.inbox.is_message_section_open,
                        "message section is not opened")
        page.inbox.find_and_open_unread_message(name=name, subject=subject)
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

    @pytest.mark.ch3
    def test_book_successful(self):
        page = FrontPage(self.driver, BASE_URL)
        page.open()

        # click on first room
        room = page.rooms.available_rooms()[0]
        page.rooms.click_book_room(room)

        # book some nights, starting today
        today = date.today()
        start_date = today
        total_nights = 2
        end_date = today+timedelta(days=total_nights)
        page.rooms.select_calendar_dates(
            start_day=start_date.day, end_day=end_date.day)

        # check displayed information on the total nights and price, before submitting
        price_per_night = self.booker_api.get_rooms()[0]['roomPrice']
        total_price = price_per_night*total_nights
        page.rooms.select_calendar_dates(
            start_day=start_date.day, end_day=end_date.day)
        for selection_block in page.rooms.get_date_selection_blocks():
            self.assertEqual(selection_block.text,
                             f'{total_nights} night(s) - £{total_price}')

        # submit booking request
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.valid_email()
        phone = fake.valid_phone()
        page.rooms.fill_booking_contact_data(
            first_name=first_name, last_name=last_name, email=email, phone=phone)
        page.rooms.click_submit_booking()

        # check confirmation message and stored booking on system
        last_booking = self.booker_api.get_bookings()[-1]
        self.assertEqual(page.rooms.booking_confirmed_message,
                         f"Booking Successful!\nCongratulations! Your booking has been confirmed for:\n{start_date_str} - {end_date_str}\nClose")
        self.assertTrue(last_booking['firstname'] == first_name and last_booking['lastname'] == last_name and last_booking['bookingdates']['checkin']
                        == start_date_str and last_booking['bookingdates']['checkout'] == end_date_str, f"booking not found (last_booking={last_booking}")


################

HEADLESS = False

config = ConfigParser()
config.read('config.ini')
BASE_URL = os.environ.get("BASE_URL", config.get('app', 'base_url'))
BOOKER_API_USERNAME = config.get('app', 'booker_api_username')
BOOKER_API_PASSWORD = config.get('app', 'booker_api_password')

debugger = pdb.Pdb(stdout=sys.stdout)

fake = Faker()
fake.add_provider(MyContactProvider)
# Enforce a specific seed; there are currently some limitations in both AltWalker and GraphWalker though
# seed works in GW 4.3 but AltWaker doesn't have a way to enforce it or obtain it
seed = os.environ.get("SEED", config.getint('other', 'seed'))
print(f'seed: {seed}')
Faker.seed(int(seed))
