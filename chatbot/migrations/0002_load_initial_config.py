from django.db import migrations

def load_config(apps, schema_editor):
    ChatConfig = apps.get_model('chatbot', 'ChatConfig')
    ChatConfig.objects.get_or_create(pk=1)

class Migration(migrations.Migration):
    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_config),
    ]
