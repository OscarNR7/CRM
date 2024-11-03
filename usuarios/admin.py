from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(UserRole)

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'target', 'app_name', 'timestamp')
    list_filter = ('action', 'app_name', 'user')
    search_fields = ('user__username', 'action', 'target')
    ordering = ('-timestamp',)