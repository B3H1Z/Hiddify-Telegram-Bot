from config import *


# Document: https://github.com/hiddify/hiddify-config/discussions/3209
# It not in use now, but it will be used in the future.

class API:
    def __init__(self, url):
        self.url = url

    def select(self, endpoint):
        try:
            response = requests.get(self.url + endpoint)
            return response.json()
        except Exception as e:
            print(e)
            return None

    def find(self, endpoint, data):
        try:
            response = requests.get(self.url + endpoint, data=data)
            return response.json()
        except Exception as e:
            print(e)
            return None

    def insert(self, endpoint, data):
        try:
            response = requests.post(self.url + endpoint, data=data)
            return response.json()
        except Exception as e:
            print(e)
            return None

    def update(self, endpoint, data):
        try:
            response = requests.post(self.url + endpoint, data=data)
            return response.json()
        except Exception as e:
            print(e)
            return None

# api = API(PANEL_URL+API_PATH)
# api.select("/user/")
# api.find("/user/", {"uuid": "6ebd2ea8-4d41-48b7-8fc2-7d6570"})
# api.insert("/user/", {"example": "data"})
# api.update("/user/", {"example": "data"})
