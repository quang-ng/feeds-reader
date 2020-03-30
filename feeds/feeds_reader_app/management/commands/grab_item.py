from django.core.management.base import BaseCommand
from django.utils import timezone
from feeds_reader_app.utils import read_feed

class Command(BaseCommand):
    help = 'Grab item from URL'

    def add_arguments(self, parser):
        parser.add_argument('urls', type=str, help='The feed urls (separated by comma) ')
        parser.add_argument('result_log_path', type=str, help='The feed urls (separated by comma) ')

    def handle(self, *args, **kwargs):
        urls = kwargs['urls']
        result_log_path = kwargs['result_log_path']
        list_url = urls.split(',')

        with open(result_log_path, 'a') as log_file:
            for url in list_url:
                read_feed(url, log_file)
