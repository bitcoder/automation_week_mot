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
from datetime import date, datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
from faker import Faker
from faker.providers import BaseProvider
from tests.my_contact_provider import MyContactProvider

class BookerAPI:

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._auth = HTTPBasicAuth(self._username, self._password)

    def get_rooms(self):
        data = requests.get(f'{BASE_URL}/room', auth=self._auth)
        return data.json()['rooms']

    def get_bookings(self):
        data = requests.get(f'{BASE_URL}/booking', auth=self._auth)
        return data.json()['bookings']


class ContactFormTestCase(unittest.TestCase):

    def setUp(self):
        options = Options()
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(15)
        self.driver.maximize_window()
        # self.driver.get(BASE_URL)

        self.booker_api = BookerAPI(username="admin", password="password")

    def tearDown(self):
        self.driver.quit()

    def test_contact_form_successful(self):
        page = FrontPage(self.driver, BASE_URL)
        page.open()
        page.contact_form.wait_for_region_to_load()
        page.contact_form.fill_contact_data(name="sergio", email="sergio.freire@example.com", phone="+1234567890",
                                            subject="doubt", description="Can I book rooms up to 2 months ahead of time?")
        self.assertEqual(page.contact_form.contact_feedback_message,
                         f"Thanks for getting in touch sergio!\nWe'll get back to you about\ndoubt\nas soon as possible.")

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

    @pytest.mark.xpto
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
        first_name = "Sergio"
        last_name = "Freire"
        email = "sergio.freire@example.com"
        phone = "12345679012345"
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
BASE_URL = os.environ.get("BASE_URL", "https://aw1.automationintesting.online")
debugger = pdb.Pdb(stdout=sys.stdout)

fake = Faker()
fake.add_provider(MyContactProvider)
# Enforce a specific seed; there are currently some limitations in both AltWalker and GraphWalker though
# seed works in GW 4.3 but AltWaker doesn't have a way to enforce it or obtain it
seed = os.environ.get("SEED", 1234)
print(f'seed: {seed}')
Faker.seed(seed)