from django.db.models import Q
from django.utils import timezone

from .models import Channel, Item

import feedparser as parser

import time
import datetime

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import pyrfc3339

import json

from django.conf import settings

import hashlib
from random import choice
import logging
import collections

FeedResult = collections.namedtuple('FeedResult', ['channel', 'items'])


class NullOutput(object):
    # little class for when we have no outputter
    def write(self, str):
        pass


def _customize_sanitizer(fp):
    bad_attributes = [
        "align",
        "valign",
        "hspace",
        "class",
        "width",
        "height"
    ]

    for item in bad_attributes:
        try:
            if item in fp._HTMLSanitizer.acceptable_attributes:
                fp._HTMLSanitizer.acceptable_attributes.remove(item)
        except Exception:
            logging.debug("Could not remove {}".format(item))


def get_agent():
    agent = random_user_agent()
    logging.info("using agent: {}".format(agent))
    return agent


def random_user_agent():
    return choice([
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
        "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Mozilla/5.0 (Linux; Android 5.0; SAMSUNG SM-N900 Build/LRX21V) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/2.1 Chrome/34.0.1847.76 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 6.0.1; SAMSUNG SM-G570Y Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0 Chrome/44.0.2403.133 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0"
    ])


def fix_relative(html, url):
    """ this is fucking cheesy """

    try:
        base = "/".join(url.split("/")[:3])

        html = html.replace("src='//", "src='http://")
        html = html.replace('src="//', 'src="http://')

        html = html.replace("src='/", "src='%s/" % base)
        html = html.replace('src="/', 'src="%s/' % base)

    except:
        pass

    return html


def read_feed(feed_url, output=NullOutput()):
    headers = {"User-Agent": get_agent()}  # identify ourselves
    output.write(f"\nFetching {feed_url}")

    ret = None
    try:
        ret = requests.get(feed_url, headers=headers,
                           allow_redirects=False, timeout=20)
        output.write(f"\nFetch done. Status {ret.status_code}")
    except Exception as ex:
        logging.error("Fetch feed error: " + str(ex))
        output.write("\nFetch error: " + str(ex))

    if ret.status_code < 200 or ret.status_code >= 500:
        logging.error(f"Server error fetching feed {ret.status_code}")
    elif ret.status_code == 404:
        logging.error(f"The feed could not be found")
    elif ret.status_code == 403 or ret.status_code == 410:
        logging.error(f"Feed is no longer accessible.")
    elif ret.status_code >= 400 and ret.status_code < 500:
        logging.error(f"Bad request {ret.status_code}")
    elif ret.status_code == 304:
        logging.error(f"Clearing etag/last modified due to lack of changes")
    elif ret.status_code == 301 or ret.status_code == 308:  # permenant redirect
        logging.error(f"Feed has moved but no location provided")

    # NOT ELIF, WE HAVE TO START THE IF AGAIN TO COPE WTIH 302
    # now we are not following redirects 302, 303
    if ret and ret.status_code >= 200 and ret.status_code < 300:
        return parse_feed(ret.content, output)
    return None


def parse_feed(feed_content, output=NullOutput()):
    """ Parse feed xml."""
    feed_parser_dict = None
    try:
        _customize_sanitizer(parser)
        feed_parser_dict = parser.parse(feed_content)
    except Exception as ex:
        logging.error(f"Error parsing feed {str(ex)}")

    if not feed_parser_dict:
        logging.error("Feed empty")
        return
    pub_date = datetime.datetime.fromtimestamp(time.mktime(
        feed_parser_dict.feed.get("published_parsed"))).replace(tzinfo=timezone.utc)
    last_build_date = datetime.datetime.fromtimestamp(time.mktime(
        feed_parser_dict.feed.get("updated_parsed"))).replace(tzinfo=timezone.utc)
    try:
        channel = Channel(
            title=feed_parser_dict.feed.get("title"),
            description=feed_parser_dict.feed.get("description"),
            link=feed_parser_dict.feed.get("link"),
            category=feed_parser_dict.feed.get("category"),
            copyright=feed_parser_dict.feed.get("copyright"),
            docs=feed_parser_dict.feed.get("docs"),
            language=feed_parser_dict.feed.get("language"),
            last_build_date=last_build_date,
            managing_editor=feed_parser_dict.feed.get("author"),
            pub_date=pub_date,
            web_master=feed_parser_dict.feed.get("publisher"),
            generator=feed_parser_dict.feed.get("generator"),
        )
        channel.save()

        ## Store log
        output.write(f"\n----------------------------------------------------------------")
        output.write(f"\nChannel")
        output.write(f"\nID: {channel.id}")
        output.write(f"\nTitle: {channel.title}")
        output.write(f"\nDescription: {channel.description}")
        output.write(f"\nLink: {channel.link}")
        output.write(f"\nCategory: {channel.category}")
        output.write(f"\nCopyright: {channel.copyright}")
        output.write(f"\nDocs: {channel.docs}")
        output.write(f"\nLanguage: {channel.language}")
        output.write(f"\nLast_build_date: {channel.last_build_date}")
        output.write(f"\nManaging_editor: {channel.managing_editor}")
        output.write(f"\nPub_date: {channel.pub_date}")
        output.write(f"\nWeb_master: {channel.web_master}")
        output.write(f"\nGenerator: {channel.generator}")

        entries = feed_parser_dict.entries
        items = []
        for entry in entries:
            pub_date = datetime.datetime.fromtimestamp(time.mktime(
                entry.get("published_parsed"))).replace(tzinfo=timezone.utc)
            item = Item(
                channel=channel,
                title=entry.get("title"),
                description=entry.get("summary"),
                link=entry.get("link"),
                comments=entry.get("comments"),
                pubDate=pub_date,
            )
            item.save()
            output.write(f"\n----------------------------------------------------------------")
            output.write(f"\nItem detail")
            output.write(f"\nID: {item.id}")
            output.write(f"\nChannel ID: {item.channel.id}")
            output.write(f"\nTitle: {item.title}")
            output.write(f"\nDescription: {item.description}")
            output.write(f"\nLink: {item.link}")
            output.write(f"\nComments: {item.comments}")
            output.write(f"\nPubDate: {item.pubDate}")
            items.append(item)
        return FeedResult(channel, items)
    except AttributeError as attribute_error:
        logging.error("Attribute error: %s" % str(attribute_error))
        raise attribute_error
