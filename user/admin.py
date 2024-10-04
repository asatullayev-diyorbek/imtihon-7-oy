from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'get_full_name', 'email', 'phone', 'address', 'set_image')
    list_display_links = ('set_image', 'username', 'get_full_name')
    search_fields = ('username', 'email')

    def set_image(self, obj):
        return mark_safe(f'<img src="{obj.get_image()}" width="50" height="50" style="border-radius: 50%;"/>')
    set_image.short_description = 'Image'
