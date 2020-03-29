from django.db import models

# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=1000)
    description = models.TextField()
    link = models.URLField()
    category = models.CharField(max_length=1000)
    comments = models.URLField()
    pubDate = models.DateTimeField()
