from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ClientAddress, ProducerProfile, User


class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "user_type", "phone", "is_active", "date_joined")
    list_filter = ("user_type", "is_active")
    search_fields = ("email", "first_name", "phone")
    ordering = ("-date_joined",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Dados OpalaVerde", {"fields": ("user_type", "phone")}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(ProducerProfile)
admin.site.register(ClientAddress)
