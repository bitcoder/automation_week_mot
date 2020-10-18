from pypom import Page
from pypom import Region
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains


class FrontPage(Page):
    """Interact with frontpage."""

    _admin_panel_locator = (By.LINK_TEXT, "Admin panel")

    class ContactForm(Region):

        _contact_form_name_locator = (By.ID, "name")
        _contact_form_email_locator = (By.ID, "email")
        _contact_form_phone_locator = (By.ID, "phone")
        _contact_form_subject_locator = (By.ID, "subject")
        _contact_form_description_locator = (By.ID, "description")
        _contact_form_submit_locator = (By.ID, "submitContact")
        _contact_feedback_message_locator = (
            By.XPATH, '//div[@class="row contact"]/div[@class="col-sm-5"]')
        _contact_error_message_locator = (
            By.XPATH, '//div[@class="row contact"]//div[@class="alert alert-danger"]')

        def fill_contact_data(self, name="", email="", phone="", subject="", description=""):
            self.find_element(*self._contact_form_name_locator).clear()
            self.find_element(*self._contact_form_name_locator).send_keys(name)
            self.find_element(*self._contact_form_email_locator).clear()
            self.find_element(
                *self._contact_form_email_locator).send_keys(email)
            self.find_element(*self._contact_form_phone_locator).clear()
            self.find_element(
                *self._contact_form_phone_locator).send_keys(phone)
            self.find_element(*self._contact_form_subject_locator).clear()
            self.find_element(
                *self._contact_form_subject_locator).send_keys(subject)
            self.find_element(*self._contact_form_description_locator).clear()
            self.find_element(
                *self._contact_form_description_locator).send_keys(description)
            self.find_element(*self._contact_form_submit_locator).click()

        @property
        def contact_feedback_message(self):
            return self.find_element(*self._contact_feedback_message_locator).text

        @property
        def is_error_message_present(self):
            return self.is_element_present(*self._contact_error_message_locator)

        @property
        def is_form_available(self):
            return self.is_element_present(*self._contact_form_name_locator) and self.is_element_present(*self._contact_form_email_locator) and self.is_element_present(*self._contact_form_phone_locator) and self.is_element_present(*self._contact_form_subject_locator) and self.is_element_present(*self._contact_form_description_locator) and self.is_element_present(*self._contact_form_submit_locator)

    class Rooms(Region):

        _booking_firstname_locator = (By.XPATH, '//input[@name="firstname"]')
        _booking_lastname_locator = (By.XPATH, '//input[@name="lastname"]')
        _booking_email_locator = (By.XPATH, '//input[@name="email"]')
        _booking_phone_locator = (By.XPATH, '//input[@name="phone"]')
        _booking_submit_locator = (
            By.XPATH, '//button[contains(text(), "Book")]')
        _booking_cancel_locator = (
            By.XPATH, '//button[contains(text(), "Cancel")]')
        _booking_new_booking_locator = (
            By.XPATH, '//button[contains(text(), "Book this room")]')
        _booking_book_this_room_locator = (
            By.XPATH, './/button[contains(text(), "Book this room")]')
        _booking_error_message_locator = (
            By.XPATH, '//div[@class="row hotel-room-info"]//div[@class="alert alert-danger"]')
        _booking_confirmed_message_locator = (
            By.XPATH, '//div[@class="ReactModal__Content ReactModal__Content--after-open confirmation-modal"]')
        _available_rooms_locator = (
            By.XPATH, '//div[@class="row hotel-room-info"]')

        def fill_booking_contact_data(self, first_name="", last_name="", email="", phone="", subject="", description=""):
            self.find_element(*self._booking_firstname_locator).clear()
            self.find_element(
                *self._booking_firstname_locator).send_keys(first_name)
            self.find_element(*self._booking_lastname_locator).clear()
            self.find_element(
                *self._booking_lastname_locator).send_keys(last_name)
            self.find_element(*self._booking_email_locator).clear()
            self.find_element(*self._booking_email_locator).send_keys(email)
            self.find_element(*self._booking_phone_locator).clear()
            self.find_element(*self._booking_phone_locator).send_keys(phone)

        def click_book_first_available_room(self):
            self.find_element(*self._booking_new_booking_locator).click()

        def click_book_room(self, room):
            room.find_element(*self._booking_book_this_room_locator).click()

        def click_submit_booking(self):
            self.find_element(*self._booking_submit_locator).click()

        def click_cancel_booking(self):
            self.find_element(*self._booking_cancel_locator).click()

        def select_calendar_dates(self, start_day=1, end_day=1):
            """ select dates in calendar. Note: works only for days in current month """
            src = self.driver.find_element_by_xpath(
                f'(//div[contains(@class,"rbc-date-cell") and not(contains(@class,"rbc-off-range"))])[{start_day}]')
            dst = self.driver.find_element_by_xpath(
                f'(//div[contains(@class,"rbc-date-cell") and not(contains(@class,"rbc-off-range"))])[{end_day}]')
            self.driver.execute_script("arguments[0].scrollIntoView();", src)
            action = ActionChains(self.driver)
            action.move_to_element(src).perform()
            action.drag_and_drop(src, dst).perform()

        def get_date_selection_blocks(self):
            return self.find_elements(By.XPATH, './/div[@class="rbc-event-content" and not(contains(text(),"Unavailable"))]')

        # def get_week_blocks(self):
        #    return self.find_elements(By.XPATH,'().//div[@class="rbc-row-segment"])./div[@class="rbc-event-content"]')
        #  page.rooms.find_elements(By.XPATH,'.//div[@class="rbc-row-segment"]./div[@class="rbc-event-content"]')
        # f=page.rooms.find_elements(By.XPATH,'.//div[@class="rbc-row-segment"]')
        # e=f[0]
        # width=e.value_of_css_property('max-width')
        # width_int=int(float(width.strip('%')))

        @property
        def is_error_message_present(self):
            return self.is_element_present(*self._booking_error_message_locator)

        @property
        def booking_confirmed_message(self):
            return self.find_element(*self._booking_confirmed_message_locator).text

        def available_rooms(self):
            return self.find_elements(*self._available_rooms_locator)

    @property
    def contact_form(self):
        return FrontPage.ContactForm(self)

    @property
    def rooms(self):
        return FrontPage.Rooms(self)

    def click_admin_panel(self):
        self.find_element(*self._admin_panel_locator).click()
