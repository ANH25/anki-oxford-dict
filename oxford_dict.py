import requests

class ODError(Exception):
    pass

class ODConnectionError(ODError):
    pass

class ODWordNotFound(ODError):
    pass

class OxfordDict:

    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_word_data(self, word, lang='en-gb'):
        url = 'https://od-api.oxforddictionaries.com/api/v2/entries/' + lang + '/' + word + '?strictMatch=false'
        try:
            r = requests.get(url, headers = {'app_id': self.app_id, 'app_key': self.app_key})
        except requests.exceptions.RequestException:
            raise ODConnectionError("connection failed")
        if r.status_code == 404:
            raise ODWordNotFound(f"'{word}' not found in the dictionary")
        return r.json()
