from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Extend UserAdmin to show custom fields if needed
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'student_class', 'children', 'metadata')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'student_class', 'children', 'metadata')}),
    )

admin.site.register(User, CustomUserAdmin)
