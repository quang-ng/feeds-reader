from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.conf import settings

from .models import Channel, Item, ChannelForm, ItemForm

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

def detail_channel(request, channel_id):
    channel = get_object_or_404(Channel, pk=channel_id)
    return render(request, 'feeds_reader_app/detail.html', {'channel': channel})

def edit_channel(request, channel_id):
    item = get_object_or_404(Channel, pk=channel_id)
    if request.method == "POST":
        form = ChannelForm(request.POST or None, instance=item)
        if form.is_valid():
            form.save()
            return redirect('/feeds/' + str(item.id) + '/')
        return render(request, 'feeds_reader_app/edit_channel.html', {'form': form})

    form = ChannelForm(instance=item)
    return render(request, 'feeds_reader_app/edit_channel.html', {'form': form})

def items(request, channel_id):
    item_list = Item.objects.filter(channel_id=channel_id)
    page = request.GET.get('page', 1)

    paginator = Paginator(item_list, settings.PAGE_SIZE)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    return render(request, 
        'feeds_reader_app/list_items.html', 
        { 'items': items, "channel_id": channel_id })

def detail_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'feeds_reader_app/detail_item.html', {'item': item})

def edit_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == "POST":
        form = ItemForm(request.POST or None, instance=item)
        if form.is_valid():
            form.save()
            return redirect('/feeds/detail_item/' + str(item.id) + '/')
        return render(request, 'feeds_reader_app/edit_item.html', {'form': form})

    form = ItemForm(instance=item)
    return render(request, 'feeds_reader_app/edit_item.html', {'form': form})
