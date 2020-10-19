from pypom import Page
from pypom import Region
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class AdminPage(Page):
    """Interact with adminpage."""

    _rooms_menu_locator = (By.XPATH, '//a[@href="#/admin/"]')
    _frontpage_menu_locator = (By.ID, "frontPageLink")
    _inbox_menu_locator = (By.XPATH, '//a[@href="#/admin/messages"]')
    _logout_menu_locator = (By.LINK_TEXT, "Logout")

    _login_username_locator = (By.ID, "username")
    _login_password_locator = (By.ID, "password")
    _login_submit_locator = (By.ID, "doLogin")

    VALID_ADMIN_USERNAME = "admin"
    VALID_ADMIN_PASSWORD = "password"
    

    class Inbox(Region):

        _message_section_locator = (
        By.XPATH, '//div[@class="messages"]//div/p[contains(text(),"Subject")]')

        _message_details_name_locator = (
            By.XPATH, '//div[@class="ReactModal__Content ReactModal__Content--after-open message-modal"]/div[@class="form-row"]/div[1]')
        _message_details_phone_locator = (
            By.XPATH, '//div[@class="ReactModal__Content ReactModal__Content--after-open message-modal"]/div[@class="form-row"]/div[2]')
        _message_details_email_locator = (
            By.XPATH, '//div[@class="ReactModal__Content ReactModal__Content--after-open message-modal"]/div[@class="form-row"][2]')
        _message_details_subject_locator = (
            By.XPATH, '//div[@class="ReactModal__Content ReactModal__Content--after-open message-modal"]/div[@class="form-row"][3]')
        _message_details_description_locator = (
            By.XPATH, '//div[@class="ReactModal__Content ReactModal__Content--after-open message-modal"]/div[@class="form-row"][4]')
        _message_details_close_button_locator = (
            By.XPATH, '//button[contains(text(),"Close")]')

        @property
        def is_message_section_open(self):
            return self.is_element_present(*self._message_section_locator)

        @property
        def contains_message(self, name="", email="", phone="", subject="", message=""):
            return self.find_element(*self._message_details_name_locator).text == name and self.find_element(*self._message_details_name_locator).text == email and self.find_element(*self._message_details_phone_locator).text == phone and self.find_element(*self._message_details_subject_locator).text == subject and self.find_element(*self._message_details_description_locator).text == message

        @property
        def message_detail_name(self):
            return self.find_element(*self._message_details_name_locator).text

        @property
        def message_detail_email(self):
            return self.find_element(*self._message_details_email_locator).text

        @property
        def message_detail_phone(self):
            return self.find_element(*self._message_details_phone_locator).text

        @property
        def message_detail_subject(self):
            return self.find_element(*self._message_details_subject_locator).text

        @property
        def message_detail_description(self):
            return self.find_element(*self._message_details_description_locator).text

        def find_and_open_unread_message(self, name="", subject=""):
            self.driver.find_element_by_xpath(
                f'//div[@class="messages"]/div[contains(@class,"detail") and contains(@class,"read-false")]//p[contains(text(),"{name}")]/parent::div/following-sibling::div/p[contains(text(),"{subject}")]').click()

        def close_message_details(self):
            return self.find_element(*self._message_details_close_button_locator).click()

    class Rooms(Region):

        _rooms_section_locator = (By.XPATH, '(//div[@class="row"])//div/p[contains(text(),"Room #")]')

        @property
        def is_rooms_section_open(self):
            return self.is_element_present(*self._rooms_section_locator)


    @property
    def number_of_unread_messages(self):
        return self.find_element(*self._inbox_menu_locator).text

    def click_frontpage(self):
        self.find_element(*self._frontpage_menu_locator).click()

    def click_rooms(self):
        self.find_element(*self._rooms_menu_locator).click()

    def click_inbox(self):
        self.find_element(*self._inbox_menu_locator).click()

    def click_logout(self):
        self.find_element(*self._logout_menu_locator).click()

    def authenticate(self, username="", password=""):
        self.find_element(*self._login_username_locator).clear()
        self.find_element(*self._login_username_locator).send_keys(username)
        self.find_element(*self._login_password_locator).clear()
        self.find_element(*self._login_password_locator).send_keys(password)
        self.find_element(*self._login_submit_locator).click()
    
    def authenticate_with_valid_credentials(self):
        self.authenticate(username=self.VALID_ADMIN_USERNAME, password=self.VALID_ADMIN_PASSWORD)

    @property
    def is_login_form_available(self):
        return self.is_element_present(*self._login_username_locator) and self.is_element_present(*self._login_password_locator) and self.is_element_present(*self._login_submit_locator)

    @property
    def inbox(self):
        return AdminPage.Inbox(self)

    @property
    def rooms(self):
        return AdminPage.Rooms(self)


