from django.contrib import admin
from .models import Template, TemplateImage, TemplateService


class TemplateImageInline(admin.TabularInline):
    model = TemplateImage
    extra = 1
    fields = ('image', 'is_default', 'alt_text', 'position')


class TemplateServiceInline(admin.TabularInline):
    model = TemplateService
    extra = 1
    fields = ('service', 'position')


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'professional', 'is_active', 'created_at')
    list_filter = ('is_active', 'professional')
    search_fields = ('title', 'description', 'professional__user__username')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TemplateImageInline, TemplateServiceInline]
    fieldsets = (
        (None, {
            'fields': ('professional', 'title', 'slug', 'description', 'is_active')
        }),
    )


@admin.register(TemplateImage)
class TemplateImageAdmin(admin.ModelAdmin):
    list_display = ('template', 'is_default', 'position')
    list_filter = ('is_default', 'template')
    search_fields = ('template__title', 'alt_text')
    fields = ('template', 'image', 'is_default', 'alt_text', 'position')


@admin.register(TemplateService)
class TemplateServiceAdmin(admin.ModelAdmin):
    list_display = ('template', 'service', 'position')
    list_filter = ('template', 'service')
    search_fields = ('template__title', 'service__title')
    fields = ('template', 'service', 'position')

