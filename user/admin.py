from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Add age and gender fields to the admin panel
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('age', 'gender')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('age', 'gender')}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'age', 'gender', 'is_staff']
    search_fields = ['username', 'email']
    ordering = ['username']

admin.site.register(CustomUser, CustomUserAdmin)
