from django import forms

import django_filters
from .models import Channel, Item

class ChannelFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Channel
        fields = ('title',)