from django.contrib import admin
from .models import StudentProgress, XPTransaction
@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'xp_balance',
        'level',
        'last_activity_at',
        'created_at',
    )

    list_select_related = ('student',)

    search_fields = (
        'student__username',
        'student__first_name',
        'student__last_name',
        'student__email',
    )

    list_filter = (
        'level',
        'created_at',
    )

    readonly_fields = (
        'student',
        'xp_balance',
        'level',
        'last_activity_at',
        'created_at',
    )

    ordering = ('-xp_balance',)

    def has_add_permission(self, request):
        # Progress qo‘lda qo‘shilmaydi
        return False
@admin.register(XPTransaction)
class XPTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'amount',
        'source',
        'submission',
        'created_at',
    )

    list_select_related = ('student',)

    search_fields = (
        'student__username',
        'student__first_name',
        'student__last_name',
    )

    list_filter = (
        'source',
        'created_at',
    )

    readonly_fields = (
        'student',
        'amount',
        'source',
        'submission',
        'created_at',
    )

    ordering = ('-created_at',)

    def has_add_permission(self, request):
        # XPTransaction faqat avtomatik yaratiladi
        return False

    def has_change_permission(self, request, obj=None):
        # Audit log o‘zgartirilmaydi
        return False

    def has_delete_permission(self, request, obj=None):
        # Audit log o‘chirilmaydi
        return False
