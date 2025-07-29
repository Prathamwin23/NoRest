from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import User, Client, Assignment, LocationHistory, NotificationLog, SystemSettings

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_active_agent', 'last_login')
    list_filter = ('role', 'is_active', 'is_active_agent')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Field Operations', {
            'fields': ('role', 'phone', 'current_location', 'is_active_agent')
        }),
    )

class ClientAdmin(OSMGeoAdmin):
    list_display = ('name', 'phone', 'priority', 'is_active', 'created_at')
    list_filter = ('priority', 'is_active', 'created_at')
    search_fields = ('name', 'phone', 'email')

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('agent', 'client', 'status', 'assigned_at', 'completed_at')
    list_filter = ('status', 'assigned_at')
    search_fields = ('agent__username', 'client__name')

# Register models
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(LocationHistory)
admin.site.register(NotificationLog)
admin.site.register(SystemSettings)

admin.site.site_header = "Field Operations Management"
admin.site.site_title = "Field Operations"
