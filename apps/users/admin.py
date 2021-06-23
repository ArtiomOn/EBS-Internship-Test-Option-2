from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.users.models import CustomUser


# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    list_display = ['id', 'email']
