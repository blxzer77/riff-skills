import requests


class ProductionHttpClient:
    def post(self, url, json, timeout):
        return requests.post(url, json=json, timeout=timeout, allow_redirects=True)
