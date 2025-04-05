
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

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('property_type', 'offer_type', 'price', 'city', 'owner', 'created_at')
    list_filter = ('property_type', 'offer_type', 'city')
    search_fields = ('description', 'city', 'district')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

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
