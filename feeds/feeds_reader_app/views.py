from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.conf import settings

from .models import Channel, Item

# Create your views here.

def index(request):
    channel_list = Channel.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(channel_list, settings.PAGE_SIZE)
    try:
        channels = paginator.page(page)
    except PageNotAnInteger:
        channels = paginator.page(1)
    except EmptyPage:
        channels = paginator.page(paginator.num_pages)

    return render(request, 'feeds_reader_app/index.html', { 'channels': channels })

def detail(request, channel_id):
    channel = get_object_or_404(Channel, pk=channel_id)
    return render(request, 'feeds_reader_app/detail.html', {'channel': channel})