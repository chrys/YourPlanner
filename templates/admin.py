from django.contrib import admin
from .models import Template, TemplateImage
from django.utils.translation import gettext_lazy as _

class TemplateImageInline(admin.TabularInline):
    model = TemplateImage
    extra = 1 # Number of empty forms to display
    fields = ('image', 'is_default')
    verbose_name = _("Image")
    verbose_name_plural = _("Images")

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'professional', 'created_at', 'updated_at')
    list_filter = ('professional', 'created_at')
    search_fields = ('title', 'description', 'professional__user__username')
    inlines = [TemplateImageInline]
    fieldsets = (
        (None, {
            'fields': ('professional', 'title', 'description')
        }),
        (_('Services'), {
            'fields': ('services',)
        }),
    )
    filter_horizontal = ('services',) # For a better ManyToMany experience

@admin.register(TemplateImage)
class TemplateImageAdmin(admin.ModelAdmin):
    list_display = ('template', 'image_thumbnail', 'is_default', 'created_at')
    list_filter = ('template', 'is_default')
    search_fields = ('template__title',)
    readonly_fields = ('image_thumbnail',)

    def image_thumbnail(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return _("No image")
    image_thumbnail.short_description = _("Thumbnail")
