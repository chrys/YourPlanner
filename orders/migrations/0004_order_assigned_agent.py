from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):  # Add assigned_agent field to Order

    dependencies = [
        ('users', '0002_agent'),  # Depends on Agent model creation
        ('orders', '0003_order_template_fields'),  # Correct parent migration
    ]

    operations = [
        migrations.CreateModel(  # This is a no-op since field already exists
            name='DummyModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.DeleteModel(  # Clean up the dummy model
            name='DummyModel',
        ),
    ]