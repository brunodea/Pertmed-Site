from pertmed_site.md_manager.models import Doctor, PhoneNumber, ItemField
from django.contrib import admin


class FieldInline(admin.TabularInline):
    model = ItemField
    extra = 3

class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 3
