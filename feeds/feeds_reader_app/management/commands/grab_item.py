from django.core.management.base import BaseCommand
from django.utils import timezone
from feeds_reader_app.utils import read_feed

class Command(BaseCommand):
    help = 'Grab item from URL'

    def add_arguments(self, parser):
        parser.add_argument('urls', type=str, help='The feed urls (separated by comma) ')

    def handle(self, *args, **kwargs):
        urls = kwargs['urls']
        list_url = urls.split(',')
        for url in list_url:
            self.stdout.write("url: %s" % url)
            read_feed(url, self.stdout)
