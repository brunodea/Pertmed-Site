from pertmed_site.md_manager.models import Doctor, Item, Field, PhoneNumber
from django.contrib import admin


class FieldInline(admin.TabularInline):
    model = Field
    extra = 3

class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 3

class ItemInline(admin.TabularInline):
    model = Item
    extra = 3

class ItemAdmin(admin.ModelAdmin):
    inlines = [FieldInline]
    list_display = ('name',)

class MDAdmin(admin.ModelAdmin):
    inlines = [ItemInline, PhoneNumberInline]
    list_display = ('name',)
    search_fields = ['name']

class UserAdmin(admin.ModelAdmin): pass


admin.site.register(Item, ItemAdmin)
admin.site.register(Doctor, MDAdmin)
