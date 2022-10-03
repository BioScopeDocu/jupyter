import requests

class API_server:
    """
        Class to communicate with the API
        :param token: User token
        """
    def __init__(self, token=""):
        self.baseurl = "https://acceptatie-fieldscout.bioscope.nl/api"
        self.token = token
        self.field_id = 9999
        self.extra = ""

    def url_builder(self, name):
        url = self.baseurl + "/" + name
        if self.field_id != 9999:
            url = url + "/" + self.field_id
        if self.extra != "":
            url = url + "/" + self.extra
        return url

    def get_request(self, name):
        """
               Function for get request
               :param name: Request name
               """
        url = self.url_builder(name)
        headers = {"Authorization": "Bearer " + self.token}
        par = ""
        response = requests.get(url, headers=headers, params=par)
        print("GET", url, response.reason, response.status_code)
        if response.headers['Content-Type'] == "application/json":
            return response.json()['data']
        else:
            return False

    def post_user(self, credits):
        url = self.baseurl + "/users/login"

        response = requests.post(url, json=credits)
        print("POST", url, response.reason, response.status_code)
        if response.headers['Content-Type'] == "application/json":
            return response.json()['data']
        return response

    def post_request(self, name, fieldid=9999, extra=""):
        url = self.baseurl + "/users/login"
        headers = {"Authorization": "Bearer " + self.token}
        par = ""
        response = requests.post(url, headers=headers, params=par)
        print("POST", url, response.reason, response.status_code)
        if response.headers['Content-Type'] == "application/json":
            return response.json()['data']
        return False

