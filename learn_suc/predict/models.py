from django.db import models


# Create your models here.

"""
Original schema
"""
# class Type(models.Model):
#     id = models.BigIntegerField(primary_key=True)
#     name = models.CharField(max_length=200)
#
#     class Meta:
#         indexes = [
#             models.Index(
#                 fields=['name'],
#                 name='type_name_idx',
#             ),
#         ]
#
#
# class Item(models.Model):
#     id = models.BigIntegerField(primary_key=True)
#     name = models.CharField(max_length=500)
#     type = models.ForeignKey(Type, on_delete=models.PROTECT)
#     notes = models.TextField()
#
#     class Meta:
#         indexes = [
#             models.Index(
#                 fields=['name'],
#                 name='item_name_idx',
#             ),
#         ]
#
#
# class Embedding(models.Model):
#     item = models.OneToOneField(Item, primary_key=True, on_delete=models.PROTECT)
#     embedding = models.TextField()


"""
Performance schema
"""
class Item(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000)
    name_fl = models.CharField(max_length=2)
    type = models.SmallIntegerField()
    embedding = models.CharField(max_length=2000)

    class Meta:
        indexes = [
            models.Index(
                fields=['name'],
                name='item_name_index',
            ),
            models.Index(
                fields=['name_fl'],
                name='item_name_fl_index',
            ),
            models.Index(
                fields=['type'],
                name='item_type_index',
            ),
            models.Index(
                fields=['name_fl', 'type'],
                name='item_name_fl_type_index',
            ),
            models.Index(
                fields=['type', 'name_fl'],
                name='item_type_name_fl_index',
            ),
        ]
