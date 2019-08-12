import json
from datetime import datetime
from pprint import pprint as pp

import feedparser
import osascript
import requests
from bs4 import BeautifulSoup

URL = 'https://www.wykop.pl/rss/'
TAGS_BLACKLIST = [
    'neuropa', 'tvpis', 'tusk', 'bekazpisu', '4konserwy', 'izrael',
    'bekazlewactwa', 'bekazprawakow', 'antifa', 'wykopefekt', 'dobrazmiana',
    'lewackalogika', 'wypadek'
]

TAGS_BOOSTED = [
    'ciekawostki', 'historia', 'nauka', 'qualitycontent'
]


# def should_post(tags):
#     tags_num = len(tags)
#     removed_tags = list(set(tags).intersection(TAGS_BLACKLIST))
#     print('tags: {}'.format(tags))
#     print('removed tags: {}'.format(removed_tags))


#     print(f'tags overall: {tags_num}')
#     return 0

def make_filename():
    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    return f'wykop_{date}.json'


def dump_to_file(data):
    fname = make_filename()
    fhandler = open(fname, 'w')
    json.dump(data, fhandler)
    fhandler.close()

    return fname


def get_link_data(url):
    page = requests.get(url)
    page.raise_for_status()

    page_body = page.content
    soup = BeautifulSoup(page_body, 'html.parser')

    return (
        extract_target_url(soup),
        extract_votes(soup),
        extract_tags(soup)
    )


def extract_tags(soup_body):
    links = soup_body.select('div.fix-tagline a.tag.affect.create')
    return [link.text.replace('#', '') for link in links]


def extract_target_url(soup_body):
    links = soup_body.select('div.fix-tagline span.tag.create a.affect')
    return links[0].attrs['href']


def extract_votes(soup_body):
    return 123


def get_feed():
    response = requests.get(URL)
    return response.content


if __name__ == '__main__':
    LINKS_FETCHED = 0
    LINKS_STACK = []

    result = feedparser.parse(get_feed())

    for e in result.entries:
        url, votes, tags = get_link_data(e.link)

        data = {
            'url': url,
            'title': e.title,
            'tags': tags,
        }
        LINKS_STACK.append(data)
    output_filename = dump_to_file(LINKS_STACK)

    osascript.run(f'display notification "Dumped to file: {output_filename}" with title "wyko.py" subtitle "Fetched OK"')
