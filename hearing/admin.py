from django.contrib import admin
from .models import UserRole, Hearing, HearingUpdate


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    search_fields = ['user__username', 'role']
    list_filter = ['role']


@admin.register(Hearing)
class HearingAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'title', 'advocate', 'client', 'status', 'hearing_date']
    search_fields = ['case_number', 'title', 'description']
    list_filter = ['status', 'hearing_date', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Hearing Details', {
            'fields': ('title', 'description', 'case_number', 'hearing_date', 'location', 'status')
        }),
        ('Participants', {
            'fields': ('advocate', 'client')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HearingUpdate)
class HearingUpdateAdmin(admin.ModelAdmin):
    list_display = ['title', 'hearing', 'update_type', 'updated_by', 'is_important', 'created_at']
    search_fields = ['title', 'description', 'hearing__case_number']
    list_filter = ['update_type', 'is_important', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Update Details', {
            'fields': ('hearing', 'updated_by', 'update_type', 'title', 'description')
        }),
        ('Settings', {
            'fields': ('is_important', 'visible_to_advocate', 'visible_to_client')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
