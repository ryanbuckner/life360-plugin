import requests
import json


class life360:
    base_url = "https://api-cloudfront.life360.com/v3/"
    base_url_v4 = "https://api-cloudfront.life360.com/v4/"
    token_url = "oauth2/token"
    circles_url = "circles"
    circle_url = "circles/"

    CLIENT_TOKEN = "Y2F0aGFwYWNyQVBoZUtVc3RlOGV2ZXZldnVjSGFmZVRydVl1ZnJhYzpkOEM5ZVlVdkE2dUZ1YnJ1SmVnZXRyZVZ1dFJlQ1JVWQ=="

    def __init__(self, authorization_token=None, username=None, password=None):
        self.authorization_token = authorization_token
        self.username = username
        self.password = password
        self.access_token = None
        self.token_type = "Bearer"

    def make_request(self, url, params=None, method='GET', authheader=None):
        headers = {
            'Accept': 'application/json',
            'cache-control': 'no-cache',
            'user-agent': 'com.life360.android.safetymapd/KOKO/23.50.0 android/13',
        }
        if authheader:
            headers['Authorization'] = authheader

        if method == 'GET':
            r = requests.get(url, headers=headers)
        elif method == 'POST':
            r = requests.post(url, data=params, headers=headers)

        return r.json()

    def authenticate(self):
        url = self.base_url + self.token_url
        params = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }

        r = self.make_request(url=url, params=params, method='POST', authheader="Basic " + self.CLIENT_TOKEN)
        try:
            self.token_type = r['token_type']
            self.access_token = r['access_token']
            return True
        except:
            return False

    def get_circles(self):
        url = self.base_url_v4 + self.circles_url
        authheader = self.token_type + " " + self.access_token
        r = self.make_request(url=url, method='GET', authheader=authheader)
        return r['circles']

    def get_circle(self, circle_id):
        url = self.base_url + self.circle_url + circle_id
        authheader = self.token_type + " " + self.access_token
        r = self.make_request(url=url, method='GET', authheader=authheader)
        return r
