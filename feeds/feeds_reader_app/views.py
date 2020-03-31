from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.conf import settings

from .models import Channel, Item, ChannelForm, ItemForm
from .filters import ChannelFilter


def index(request):
    query = Channel.objects.all()
    channel_filter = ChannelFilter(request.GET, queryset=query)
    channel_list = channel_filter.qs
    form = channel_filter.form

    page = request.GET.get('page', 1)
    paginator = Paginator(channel_list, settings.PAGE_SIZE)

    try:
        channels = paginator.page(page)
    except PageNotAnInteger:
        channels = paginator.page(1)
    except EmptyPage:
        channels = paginator.page(paginator.num_pages)

    return render(request, 'feeds_reader_app/index.html',
                  {'channels': channels, "channel_form": form})


def detail_channel(request, channel_id):
    channel = get_object_or_404(Channel, pk=channel_id)
    return render(request, 'feeds_reader_app/detail.html', {'channel': channel})

def delete_channel(request, channel_id):
    Channel.objects.filter(id=channel_id).delete()
    return redirect('/feeds/')

def delete_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    channel = item.channel

    Item.objects.filter(id=item_id).delete()
    return redirect('/feeds/items/' + str(channel.id) + '/')

def edit_channel(request, channel_id=None):
    if channel_id:
        channel = get_object_or_404(Channel, pk=channel_id)
    else:
        channel = Channel()
    if request.method == "POST":
        form = ChannelForm(request.POST or None, instance=channel)
        if form.is_valid():
            form.save()
            return redirect('/feeds/' + str(channel.id) + '/')
        return render(request, 'feeds_reader_app/edit_channel.html', {'form': form})

    form = ChannelForm(instance=channel)
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
                  {'items': items, "channel_id": channel_id})


def detail_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'feeds_reader_app/detail_item.html', {'item': item})


def edit_item(request, item_id=None, channel_id=None):
    print("chh: ", channel_id)
    if item_id:
        item = get_object_or_404(Item, pk=item_id)
    else:
        item = Item()
        item.channel = get_object_or_404(Channel, pk=channel_id)
    
    if request.method == "POST":
        form = ItemForm(request.POST or None, instance=item)
        if form.is_valid():
            form.save()
            return redirect('/feeds/detail_item/' + str(item.id) + '/')
        return render(request, 'feeds_reader_app/edit_item.html', {'form': form})

    form = ItemForm(instance=item)
    return render(request, 'feeds_reader_app/edit_item.html', {'form': form})
