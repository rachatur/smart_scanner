from django.db import connections
from django.db import models


class Item(models.Model):
    item_num = models.CharField(max_length=100)
    # subinventory_code = models.CharField(max_length=100)

    def __str__(self):
        return self.item_num




# class Student(models.Model):
#     roll = models.CharField(max_length=100)
#     sclass = models.CharField(max_length=100)
#     fname = models.CharField(max_length=100)
#     lname = models.CharField(max_length=100)
#     class Meta:
#         db_table = "students"

