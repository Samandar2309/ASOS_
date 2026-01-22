from django.contrib import admin
from .models import Group, GroupStudent


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'subject',
        'center',
        'teacher',
        'invite_code',
        'is_active',
        'created_at',
    )
    list_filter = (
        'center',
        'subject',
        'is_active',
    )
    search_fields = (
        'name',
        'subject',
        'invite_code',
        'teacher__username',
        'teacher__first_name',
        'teacher__last_name',
    )
    ordering = ('-created_at',)

    readonly_fields = ('invite_code', 'created_at')

    fieldsets = (
        ('Asosiy maʼlumotlar', {
            'fields': ('name', 'subject', 'center', 'teacher')
        }),
        ('Taklif kodi', {
            'fields': ('invite_code',)
        }),
        ('Holat', {
            'fields': ('is_active',)
        }),
        ('Vaqt', {
            'fields': ('created_at',)
        }),
    )


@admin.register(GroupStudent)
class GroupStudentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'group',
        'joined_at',
    )
    list_filter = (
        'group__center',
        'group',
    )
    search_fields = (
        'student__username',
        'student__first_name',
        'student__last_name',
        'group__name',
    )
    ordering = ('-joined_at',)

    readonly_fields = ('joined_at',)
