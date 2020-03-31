from django.db import models
from django.forms import ModelForm


class Channel(models.Model):
    """Channel object in feed."""

    title = models.CharField(
        max_length=1000, default=None, blank=True, null=True)
    description = models.TextField(default=None, blank=True, null=True)
    link = models.URLField(default=None, blank=True, null=True)
    category = models.CharField(
        max_length=1000, default=None, blank=True, null=True)
    copyright = models.TextField(default=None, blank=True, null=True)
    docs = models.TextField(default=None, blank=True, null=True)
    language = models.CharField(
        max_length=1000, default=None, blank=True, null=True)
    last_build_date = models.DateTimeField(default=None, blank=True, null=True)
    managing_editor = models.EmailField(default=None, blank=True, null=True)
    pub_date = models.DateTimeField(default=None, blank=True, null=True)
    web_master = models.EmailField(default=None, blank=True, null=True)
    generator = models.TextField(default=None, blank=True, null=True)


class Item(models.Model):
    """Item object in channel."""

    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    title = models.CharField(
        max_length=1000, default=None, blank=True, null=True)
    description = models.TextField(default=None, blank=True, null=True)
    link = models.URLField(default=None, blank=True, null=True)
    category = models.CharField(
        max_length=1000, default=None, blank=True, null=True)
    comments = models.URLField(default=None, blank=True, null=True)
    pubDate = models.DateTimeField(default=None, blank=True, null=True)


class ChannelForm(ModelForm):
    class Meta:
        model = Channel
        fields = '__all__'

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = '__all__'
