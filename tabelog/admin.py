from django.contrib import admin
from .models import CustomUser, Shop, Category, Review, Booking
from django.utils.safestring import mark_safe


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(CustomUser)
admin.site.register(Shop)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review)
admin.site.register(Booking)