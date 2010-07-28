from django.db import models


class Doctor(models.Model):
    name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name


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


