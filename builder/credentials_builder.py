from credentials.definitions import ROOT_DIR

import os
from dotenv import load_dotenv
import requests


class LoginBuilder:

    def __init__(self):
        self.token_url = "https://www.warcraftlogs.com/oauth/token"
        load_dotenv(os.path.join(ROOT_DIR, 'credentials', 'credentials.env'))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(exc_type)

    def get_token(self):
        data_grant = {"grant_type": "client_credentials"}
        auth = (os.environ.get("client_id"), os.environ.get("client_secret"))
        with requests.Session() as session:
            response = session.post(self.token_url, data=data_grant, auth=auth)
        return response.json().get("access_token")

    def get_header(self):
        return {"Authorization": f"Bearer {self.get_token()}"}
