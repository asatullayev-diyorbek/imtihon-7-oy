from django.contrib import admin

from .models import Category, Book, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name', )}


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('user', 'book', 'rating', 'content', 'created_at')
    readonly_fields = ('created_at', ) #'user', 'book', 'rating', 'content',


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'author', 'is_featured', 'price', 'discount', 'current_price', 'is_discount')
    list_display_links = ('id', 'title')
    prepopulated_fields = {'slug': ('title', )}
    list_editable = ('is_featured', 'price', 'is_discount', 'discount')
    inlines = [CommentInline]


