import requests
from requests.auth import HTTPBasicAuth

class BookerAPI:

    def __init__(self, base_url, username, password):
        self._base_url = base_url
        self._username = username
        self._password = password
        self._auth = HTTPBasicAuth(self._username, self._password)

    def get_rooms(self):
        data = requests.get(f'{self._base_url}/room', auth=self._auth)
        return data.json()['rooms']

    def get_bookings(self):
        data = requests.get(f'{self._base_url}/booking', auth=self._auth)
        return data.json()['bookings']