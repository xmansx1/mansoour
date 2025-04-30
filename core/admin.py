from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Property, CustomerRequest, Execution


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'phone', 'city', 'district')
    list_filter = ('user_type', 'city')
    search_fields = ('username', 'email', 'phone', 'city')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'phone', 'city', 'district', 'license_number')}),
    )


from django.utils import timezone

class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'property_type',
        'offer_type',
        'price',
        'city',
        'district',
        'status',
        'owner',
        'reserved_by',
        'reserved_at',
        'executed_by',
        'executed_at',
        'created_at',
    )
    list_filter = ('property_type', 'offer_type', 'city', 'status')
    search_fields = (
        'description',
        'city',
        'district',
        'owner__username',
        'reserved_by__username',
        'executed_by__username',
    )
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'reserved_at', 'executed_at')

    # ✅ الإجراءات (Actions)
    actions = ['mark_reserved', 'mark_executed', 'mark_available']

    @admin.action(description="🔒 تحديد كـ محجوز (مع تسجيل المستخدم والوقت)")
    def mark_reserved(self, request, queryset):
        now = timezone.now()
        count = 0
        for prop in queryset:
            if prop.status != 'reserved':
                prop.status = 'reserved'
                prop.reserved_by = request.user
                prop.reserved_at = now
                prop.executed_by = None
                prop.executed_at = None
                prop.save()
                count += 1
        self.message_user(request, f"✅ تم حجز {count} عقار/عقارات.")

    @admin.action(description="✅ تحديد كـ تم التنفيذ (مع تسجيل المستخدم والوقت)")
    def mark_executed(self, request, queryset):
        now = timezone.now()
        count = 0
        for prop in queryset:
            if prop.status != 'executed':
                prop.status = 'executed'
                prop.executed_by = request.user
                prop.executed_at = now
                prop.save()
                count += 1
        self.message_user(request, f"✅ تم تنفيذ {count} عقار/عقارات.")

    @admin.action(description="🔄 تحديد كـ متاح (وإلغاء بيانات الحجز والتنفيذ)")
    def mark_available(self, request, queryset):
        count = 0
        for prop in queryset:
            if prop.status != 'available':
                prop.status = 'available'
                prop.reserved_by = None
                prop.reserved_at = None
                prop.executed_by = None
                prop.executed_at = None
                prop.save()
                count += 1
        self.message_user(request, f"🔄 تم إعادة {count} عقار/عقارات إلى الحالة المتاحة.")



class CustomerRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'request_type', 'property_type', 'city', 'status', 'created_at')
    list_filter = ('request_type', 'property_type', 'city', 'status')
    search_fields = ('full_name', 'phone', 'details')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)


class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('customer_request', 'agent', 'executed_at')
    search_fields = ('agent__username', 'customer_request__full_name')
    date_hierarchy = 'executed_at'
    readonly_fields = ('executed_at',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(CustomerRequest, CustomerRequestAdmin)
admin.site.register(Execution, ExecutionAdmin)
