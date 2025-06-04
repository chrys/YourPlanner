from django.db import migrations

def create_initial_categories(apps, schema_editor):
    ConfigurationCategory = apps.get_model('configuration', 'ConfigurationCategory')
    
    # Create the initial categories
    categories = [
        {
            'name': 'WEBSITE',
            'description': 'Website configuration labels for general site settings.'
        },
        {
            'name': 'PROFESSIONAL',
            'description': 'Labels for Professionals. These labels will be available when adding or editing Professionals.'
        },
        {
            'name': 'SERVICE',
            'description': 'Labels for Services and Items. These labels will be available when adding or editing Services and Items.'
        },
        {
            'name': 'CUSTOMER',
            'description': 'Labels for Customers. These labels will be available when adding or editing Customers.'
        },
    ]
    
    for category_data in categories:
        ConfigurationCategory.objects.create(**category_data)


def remove_initial_categories(apps, schema_editor):
    ConfigurationCategory = apps.get_model('configuration', 'ConfigurationCategory')
    ConfigurationCategory.objects.filter(name__in=['WEBSITE', 'PROFESSIONAL', 'SERVICE', 'CUSTOMER']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_categories, remove_initial_categories),
    ]

