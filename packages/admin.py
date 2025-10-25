from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Template, TemplateImage, TemplateItemGroup, TemplateItemGroupItem  # CHANGE: Added new models

class TemplateImageInline(admin.TabularInline):
    model = TemplateImage
    extra = 1
    fields = ('image', 'is_default')
    verbose_name = _("Image")
    verbose_name_plural = _("Images")


class TemplateItemGroupItemInline(admin.TabularInline):  # CHANGE: New inline for group items
    model = TemplateItemGroupItem
    extra = 1
    fields = ('item', 'position')
    verbose_name = _("Item")
    verbose_name_plural = _("Items")
    autocomplete_fields = ['item']


class TemplateItemGroupInline(admin.StackedInline):  # CHANGE: New inline for groups
    model = TemplateItemGroup
    extra = 0
    fields = ('name', 'position', 'mandatory_count')
    verbose_name = _("Item Group")
    verbose_name_plural = _("Item Groups")
    show_change_link = True


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'professional', 'base_price', 'currency', 'default_guests', 'created_at', 'updated_at')  # CHANGE: Added pricing fields
    list_filter = ('professional', 'currency', 'created_at')  # CHANGE: Added currency filter
    search_fields = ('title', 'description', 'professional__user__username')
    inlines = [TemplateImageInline, TemplateItemGroupInline]  # CHANGE: Added TemplateItemGroupInline
    fieldsets = (
        (None, {
            'fields': ('professional', 'title', 'description')
        }),
        (_('Services'), {
            'fields': ('services',)
        }),
        (_('Pricing'), {  # CHANGE: New pricing section
            'fields': ('base_price', 'currency', 'default_guests', 'price_per_additional_guest')
        }),
    )
    filter_horizontal = ('services',)


@admin.register(TemplateItemGroup)  # CHANGE: New admin for item groups
class TemplateItemGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'position', 'mandatory_count', 'item_count')
    list_filter = ('template__professional',)
    search_fields = ('name', 'template__title')
    inlines = [TemplateItemGroupItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = _('Number of Items')


@admin.register(TemplateImage)
class TemplateImageAdmin(admin.ModelAdmin):
    list_display = ('template', 'is_default', 'created_at')
    list_filter = ('is_default', 'created_at')
    search_fields = ('template__title',)