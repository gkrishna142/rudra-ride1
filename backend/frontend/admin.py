from django.contrib import admin
from .models import PromoCode, UserProfile, AdminProfile, Zone


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    """Admin interface for PromoCode model"""
    list_display = ['code', 'discount_type', 'discount_value', 'status', 'start_date', 'expire_date', 'current_usage', 'max_usage', 'is_valid', 'created_at']
    list_filter = ['status', 'discount_type', 'start_date', 'expire_date']
    search_fields = ['code']
    readonly_fields = ['current_usage', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Promo Code Information', {
            'fields': ('code', 'status')
        }),
        ('Discount Details', {
            'fields': ('discount_type', 'discount_value')
        }),
        ('Validity Period', {
            'fields': ('start_date', 'expire_date')
        }),
        ('Usage Limits', {
            'fields': ('max_usage', 'current_usage')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(UserProfile)


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    """Admin interface for AdminProfile model"""
    list_display = ['name', 'email', 'user', 'role', 'is_active', 'created_at', 'updated_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['name', 'email', 'user__username', 'user__email']
    readonly_fields = ['password', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Admin Information', {
            'fields': ('user', 'name', 'email', 'password', 'role', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    """Admin interface for Zone model"""
    list_display = ['zone_name', 'country', 'state', 'city', 'priority', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'country', 'state', 'city', 'created_at']
    search_fields = ['zone_name', 'country', 'state', 'city']
    readonly_fields = ['zone_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Zone Information', {
            'fields': ('zone_name', 'priority', 'status')
        }),
        ('Location', {
            'fields': ('country', 'state', 'city')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


