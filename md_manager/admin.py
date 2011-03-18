from pertmed_site.md_manager.models import Doctor, PhoneNumber, ItemField, Item, Notifications
from django.contrib import admin

admin.site.register(Doctor)
admin.site.register(PhoneNumber)
admin.site.register(Item)
admin.site.register(ItemField)
admin.site.register(Notifications)
