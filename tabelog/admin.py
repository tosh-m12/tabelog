from django.contrib import admin
from .models import CustomUser, Shop, Category, Review, Booking
from django.utils.safestring import mark_safe


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name']


class ShopAdmin(admin.ModelAdmin):
    search_fields = ['name']


class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ['email']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review)
admin.site.register(Booking)