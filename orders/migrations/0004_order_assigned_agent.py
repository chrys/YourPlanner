from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):  # Add assigned_agent field to Order

    dependencies = [
        ('users', '0002_agent'),  # Depends on Agent model creation
        ('orders', '0003_order_template_fields'),  # Correct parent migration
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='assigned_agent',
            field=models.ForeignKey(blank=True, help_text='Agent assigned to handle this order', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_orders', to='users.agent'),
        ),
    ]