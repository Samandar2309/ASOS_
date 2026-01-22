from django.contrib import admin
from .models import Center, Membership


class MembershipInline(admin.TabularInline):
    """Markaz a'zolari inline ko'rinishi"""
    model = Membership
    extra = 0
    readonly_fields = ('joined_at', 'updated_at')
    fields = ('user', 'role', 'status', 'is_default', 'joined_at')
    raw_id_fields = ('user',)


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    """Markaz admin paneli"""

    list_display = (
        'name',
        'created_by',
        'status',
        'subscription_plan',
        'invite_code',
        'member_count',
        'created_at'
    )

    list_filter = (
        'status',
        'subscription_plan',
        'created_at'
    )

    search_fields = (
        'name',
        'email',
        'phone',
        'address',
        'invite_code',
        'created_by__username',
        'created_by__email'
    )

    fieldsets = (
        ('Asosiy maʼlumotlar', {
            'fields': ('name', 'description', 'invite_code')
        }),
        ('Aloqa maʼlumotlari', {
            'fields': ('email', 'phone', 'address', 'website')
        }),
        ('Sozlamalar', {
            'fields': ('status', 'subscription_plan', 'subscription_end_date')
        }),
        ('Limitlar', {
            'fields': ('max_students', 'max_teachers')
        }),
        ('Yaratuvchi', {
            'fields': ('created_by',)
        }),
        ('Sanalar', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    readonly_fields = ('invite_code', 'created_at', 'updated_at')

    inlines = [MembershipInline]

    def member_count(self, obj):
        """A'zolar soni"""
        return obj.memberships.filter(status='ACTIVE').count()

    member_count.short_description = 'Aʼzolar soni'

    def save_model(self, request, obj, form, change):
        """Yaratilayotganda created_by ni o'rnatish"""
        if not change:  # Yangi markaz yaratilayotganda
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """A'zolik admin paneli"""

    list_display = (
        'user',
        'center',
        'role',
        'status',
        'is_default',
        'joined_at'
    )

    list_filter = (
        'role',
        'status',
        'is_default',
        'joined_at',
        'center'
    )

    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'center__name'
    )

    fieldsets = (
        ('Asosiy maʼlumotlar', {
            'fields': ('user', 'center', 'role', 'status')
        }),
        ('Qoʻshimcha', {
            'fields': ('is_default', 'notes')
        }),
        ('Sanalar', {
            'fields': ('joined_at', 'updated_at')
        }),
    )

    readonly_fields = ('joined_at', 'updated_at')

    def get_queryset(self, request):
        """Querysetni optimize qilish"""
        return super().get_queryset(request).select_related('user', 'center')