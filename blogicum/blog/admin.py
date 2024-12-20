from django.contrib import admin
from django.utils.safestring import mark_safe
admin.site.empty_value_display = "Не задано"

from .models import Location, Category, Post, Comment

class BlogAdmin(admin.ModelAdmin):

    list_editable = ("is_published",)


class CommentAdmin(admin.TabularInline):

    model = Comment
    readonly_fields = (
        "text",
        "author",
        "created_at",
    )
    extra = 0

@admin.register(Post)
class PostAdmin(BlogAdmin):

    inlines = [CommentAdmin]

    list_display = (
        "title",
        "is_published",
        "pub_date",
        "author",
        "comment_count",
        "get_post_img",
    )
    search_fields = (
        "title",
        "text",
    )
    list_filter = (
        "is_published",
        "category",
        "location",
        "author",
    )
    fields = (
        "is_published",
        "title",
        "text",
        "pub_date",
        "author",
        "location",
        "category",
        "get_post_img",
        "image",
    )
    readonly_fields = ("get_post_img",)
    save_on_top = True

    @admin.display(description="Изображение")
    def get_post_img(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width=50")

    @admin.display(description="Комментарии")
    def comment_count(self, obj):
        return obj.comments.count()


@admin.register(Category)
class CategoryAdmin(BlogAdmin):

    list_display = (
        "title",
        "is_published",
        "created_at",
        "slug",
    )


@admin.register(Location)
class LocationAdmin(BlogAdmin):
    list_display = (
        "name",
        "is_published",
        "created_at",
    )
