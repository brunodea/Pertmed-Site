from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.ForeignKey(User, unique=True)
    name = models.CharField(max_length=30)    

    def __unicode__(self):
        return self.name

    def sorted_itens_fields(self):
        doc_itens = self.item_set.all()
        doc_itens = sorted(doc_itens, key=lambda item: item.name)

        doc_itens_fields = []
        for item in doc_itens:  
            doc_itens_fields.append((item, sorted(item.field_set.all(), key=lambda field: field.name)))

        return doc_itens_fields

class PhoneNumber(models.Model):
    doctor = models.ForeignKey(Doctor)
    region = models.CharField(max_length=2)
    phone = models.CharField(max_length=8)

    def __unicode__(self):
        return '(' + str(self.region) + ')' + str(self.phone)

class Item(models.Model):
    doctor = models.ForeignKey(Doctor)
    name = models.CharField(max_length=30)

    def  __unicode__(self):
        return self.name


class Field(models.Model):
    item = models.ForeignKey(Item)
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


