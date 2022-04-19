import time
import json
from urllib import response
import requests
from requests.auth import HTTPBasicAuth

class APIOctoPrint():
    def __init__(self, api_url: str, api_secret: str) -> None:
        self.api_url = api_url
        self.api_secret = api_secret

    def _create_header(self):
        headers = {
            'X-Api-Key': self.api_secret,
            'Content-Type': 'application/json'
        }
        return headers

    def get(self, endpoint: str, body: str = None) -> response:
        url = self.api_url + endpoint
        headers = self._create_header()
        return requests.get(url, headers=headers)

    def post(self, endpoint: str, body: str = None) -> response:
        url = self.api_url + endpoint

        headers = self._create_header()

        return requests.post(url, headers=headers, json=body)

    def get_api_printer(self):
        return self.get('/api/printer').json()

    def get_api_settings(self):
        return self.get('/api/settings').json()

    def get_api_job(self):
        return self.get('/api/job').json()

def main():
    api_url = 'http://192.168.0.198'
    api_secret = 'BE923FCB1F68452B9AA398D7FB51414D'
    api = APIOctoPrint(api_url=api_url, api_secret=api_secret)
    r = api.get_api_printer()
    j = api.get_api_job()
    # state_flags = r['state']['flags']
    # print(state_flags)
    # print(state_flags['printing'])

    # r = api.get_api_settings()
    print(r)
    print('space')
    print(j)
    print('space')
    fileName = j['job']['file']['name']
    print(fileName)

if __name__ == '__main__':
    main()