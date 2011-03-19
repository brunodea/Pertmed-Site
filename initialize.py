import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import md_manager.macros import infos_dic
from md_manager.models import Item, ItemField

Item.objects.all().delete()
ItemField.objects.all().delete()

for title in infos_dic.keys():
    item = Item(name=title)
    item.save()
    
    for field in infos_dic[title]:
        item_field = ItemField(item=item, name=field) 
        item_field.save()
        
