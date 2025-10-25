# Generated to add Template-first fields to Order  # [added]
from django.db import migrations, models  # [added]
import django.db.models.deletion  # [added]


class Migration(migrations.Migration):  # [added]

    dependencies = [  # [added]
        ('orders', '0002_order_unique_pending_order_per_customer'),
        ('packages', '0001_initial'),
    ]

    operations = [  # [added]
        migrations.AddField(  # [added]
            model_name='order',  # [added]
            name='template',  # [added]
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='packages.template'),  # [added]
        ),
        migrations.AddField(  # [added]
            model_name='order',  # [added]
            name='template_guest_count',  # [added]
            field=models.PositiveIntegerField(blank=True, default=0),  # [added]
        ),
        migrations.AddField(  # [added]
            model_name='order',  # [added]
            name='template_total_amount',  # [added]
            field=models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2),  # [added]
        ),
    ]  # [added]
