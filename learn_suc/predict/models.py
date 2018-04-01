from django.db import models


# Create your models here.


class Type(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=200)


class Item(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=500)
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    notes = models.TextField()


class Embedding(models.Model):
    item = models.OneToOneField(Item, primary_key=True, on_delete=models.PROTECT)
    embedding = models.TextField()
