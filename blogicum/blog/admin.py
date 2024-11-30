#  login/pass admin1/admin1
from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'text', 'pub_date',
                     'author__last_name', 'location__name',
                     'category__title')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ('name',)
