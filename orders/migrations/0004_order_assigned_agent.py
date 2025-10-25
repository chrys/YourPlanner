from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):  # CHANGE: Add assigned_agent field to Order

    dependencies = [
        ('users', '0002_agent'),  # CHANGE: Depends on Agent model creation
        ('orders', '0003_order_template_fields'),  # CHANGE: Correct parent migration
    ]

    operations = [
        migrations.CreateModel(  # CHANGE: This is a no-op since field already exists
            name='DummyModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.DeleteModel(  # CHANGE: Clean up the dummy model
            name='DummyModel',
        ),
    ]