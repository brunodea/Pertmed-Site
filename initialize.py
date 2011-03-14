import pertmed_site.md_manager.macros
from pertmed_site.md_manager.models import ItemTitle, ItemField

ItemTitle.objects.clear()
ItemField.objects.clear()

index = 0
for (title in info_items):
    itt = ItemTitle(item_name=title)
    itt.save()
    
    for(field in info_fields[index]):
        itf = ItemField(parent_item=itt, field_name=field) 
        
    index += 1