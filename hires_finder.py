from bs4 import BeautifulSoup
from re import split as re_split
import requests
import urlshortener


class Image:
    def __init__(self, hires_link, copyright_tag):
        self.hires_link = hires_link
        self.copyright_tag = copyright_tag
        self.res = None
        self.file_id = None
        self.db_id = None
        self.extra_tags = []


def iqdb_tag_match(tag):
    if tag.name == 'td':
        return True
    if not tag.has_attr('class'):
        return False
    if tag['class'] == 'image':
        return True
    return False


def get_from_danbooru(link):
    danbooru = None
    while True:  # strange cycle coz danbooru likes to fail
        danbooru = requests.request('GET', link)
        if danbooru.status_code == 200:
            break
    danbooru_soup = BeautifulSoup(danbooru.content, 'html5lib')
    copyright_tag = danbooru_soup.find('li', {'class': 'category-3'}).contents[2].string
    copyright_tag = '#' + copyright_tag.replace(' ', '_')
    hires_link = 'http://danbooru.donmai.us'
    try:
        hires_link += danbooru_soup.find(id='image-resize-link')['href']
    except TypeError:
        hires_link += danbooru_soup.find(id='image')['src']
    return Image(hires_link, copyright_tag)


def get_from_zerochan(link):
    zerochan = requests.request('GET', link)
    zerochan_soup = BeautifulSoup(zerochan.content, 'html5lib')
    hires_link = zerochan_soup.find('div', {'id': 'large'}).a['href']  # FIXME
    if hires_link:
        copyright_tag = zerochan_soup.find('h1').contents[2].string
        copyright_tag = '#' + copyright_tag.replace(' ', '_')
    else:
        return None
    return Image(hires_link, copyright_tag)


def process_tag(tag):
    if not len(tag.contents) == 5:
        return None
    similarity = int(tag.contents[4].td.string[:2])
    if similarity < 90:
        return None
    link = tag.a['href']
    if not link.startswith('http'):
        link = 'http:' + link
    source = tag.contents[2].td.contents[1]
    resolution_str = tag.contents[3].td.string.split(' ', 1)[0]
    res = re_split(r'[^\d]+', resolution_str)

    image = None
    if source == 'Danbooru ':
        image = get_from_danbooru(link)
    elif source == 'Zerochan':
        image = get_from_zerochan(link)

    if image:
        image.res = res
        return image
    return None


def get_hires(file):
    files = {'file': file}
    iqdb = requests.request('POST', 'http://iqdb.org', files=files)
    assert iqdb.status_code == 200, 'iqdb req failed'
    iqdb_soup = BeautifulSoup(iqdb.content, 'html5lib')

    image = None
    for tag in iqdb_soup.body.find_all('tbody'):
        image = process_tag(tag)
        if image:
            break

    assert image, 'hires not found'
    image.hires_link = s.shorten(image.hires_link)
    return image

s = urlshortener.Shortener()
