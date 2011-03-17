from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.ForeignKey(User, unique=True) 
    name = models.CharField(max_length=30)    

    def __unicode__(self):
        return self.name

    def sorted_itens_fields(self):
        doc_itens = self.get_itens_title()
        doc_itens = sorted(doc_itens, key=lambda item: item.name)

        doc_itens_fields = []
        for item in doc_itens:  
            doc_itens_fields.append((item, sorted(item.field_set.all(), key=lambda field: field.name)))

        return doc_itens_fields
		
	def get_itens_title(self):
		itens = []
		notifs = self.notifications_set.all()
		for notif in notfis:
			for item in notif:
				for item_title in item.itemtitle_set.all():
					if item_title not in itens:
						itens.append(item_title)
			
		return itens

class PhoneNumber(models.Model):
    doctor = models.ForeignKey(Doctor)
    region = models.CharField(max_length=2)
    phone = models.CharField(max_length=8)

    def __unicode__(self):
        return '(' + str(self.region) + ')' + str(self.phone)

#possivel implementacao

class ItemTitle(models.Model):
    item_name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name
        
class ItemField(models.Model):
    parent_item = models.ForeignKey(ItemTitle)
    field_name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.field_name
        
class Notifications(models.Model):
    doctor = models.ForeignKey(Doctor)
    field = models.ForeignKey(ItemField)
    


