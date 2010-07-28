from pertmed_site.md_manager.models import Doctor, Item, Field
from django.contrib import admin


class FieldInline(admin.TabularInline):
    model = Field
    extra = 3

class ItemInline(admin.TabularInline):
    model = Item
    extra = 3

class ItemAdmin(admin.ModelAdmin):
    inlines = [FieldInline]
    list_display = ('name',)

class MDAdmin(admin.ModelAdmin):
    inlines = [ItemInline]
    list_display = ('name',)
    search_fields = ['name']


admin.site.register(Item, ItemAdmin)
admin.site.register(Doctor, MDAdmin)
