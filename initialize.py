import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import md_manager.macros
from md_manager.models import Item, ItemField

Item.objects.all().delete()
ItemField.objects.all().delete()

for title in md_manager.macros.infos_dic.keys():
    item = Item(name=title)
    item.save()
    
    for field in md_manager.macros.infos_dic[title]:
        item_field = ItemField(item=item, name=field) 
        item_field.save()

