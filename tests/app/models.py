from django.db import models
from partitioning.decorators import partitioning


@partitioning([
    {'type': 'list', 'column': 'tag'},
    {'type': 'range_month', 'column': 'created'},
])
class Message(models.Model):
    text = models.TextField()
    tag = models.CharField(max_length=255)
    created = models.DateTimeField()
