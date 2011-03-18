from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.ForeignKey(User, unique=True) 
    name = models.CharField(max_length=30)    

    def __unicode__(self):
        return self.name

    #faz uma lista de tuplas ordenadas pelo nome do Item e 
    #uma lista com os Fields de tal Item ordenados pelo seus nomes.
    def sorted_itens_fields(self):
        itens_dic = self.get_itens_dic()
        doc_itens = sorted(itens_dic.keys())#sorted(self.item_set.all(), key=lambda item: item.name) #lista de itens do medico ordenados pelo nome.
        doc_itens_fields = []

        for item in doc_itens:
            fields = sorted(itens_dic[item], key=lambda field: field.name) #lista de field ordenada pelo nome dos fields.
            doc_itens_fields.append((item, fields))

        return doc_itens_fields
		
    def get_itens_dic(self):
        itens = {}
        notifs = self.notifications_set.all()
        for notif in notifs:
            field = ItemField.objects.get(id=notif.field.id)
            item = Item.objects.get(id=field.item.id)

            try:
                itens[item.name].append(field)
            except KeyError:
                itens[item.name] = []
                itens[item.name].append(field)

        return itens     

class PhoneNumber(models.Model):
    doctor = models.ForeignKey(Doctor)
    region = models.CharField(max_length=2)
    phone = models.CharField(max_length=8)

    def __unicode__(self):
        return '(' + str(self.region) + ')' + str(self.phone)

class Item(models.Model):
    name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name
        
class ItemField(models.Model):
    item = models.ForeignKey(Item)
    name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name
        
class Notifications(models.Model):
    doctor = models.ForeignKey(Doctor)
    field = models.ForeignKey(ItemField)

    def __unicode__(self):
        return self.doctor.name + ', field id: ' + str(self.field.id)
    


