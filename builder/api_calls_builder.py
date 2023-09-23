import requests


class CallsBuilder:
    def __init__(self):
        self.public_url = "https://www.warcraftlogs.com/api/v2/client"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(exc_type)

    def make_call(self, headers, query, **kwargs):
        data = {"query": query, "variables": kwargs}
        with requests.Session() as session:
            session.headers = headers
            response = session.get(self.public_url, json=data)
            return response.json()
