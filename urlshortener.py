import requests

shortener_url = 'https://v.gd/create.php'

class Shortener:
    def __init__(self):
        pass

    def shorten(self, long_url):
        short = requests.get(shortener_url, params={
            'format': 'simple',
            'url': long_url
        }).content
        return str(short, 'ascii')
