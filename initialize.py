import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import md_manager.macros
from md_manager.models import ItemTitle, ItemField

ItemTitle.objects.all().delete()
ItemField.objects.all().delete()

index = 0
for title in md_manager.macros.info_itens:
    itt = ItemTitle(item_name=title)
    itt.save()
    
    for field in md_manager.macros.info_fields[index]:
        itf = ItemField(parent_item=itt, field_name=field) 
        itf.save()
        
    index += 1