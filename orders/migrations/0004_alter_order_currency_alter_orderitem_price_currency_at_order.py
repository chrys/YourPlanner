from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_orderstatushistory_alter_orderitem_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='currency',
            field=models.CharField(blank=True, default='EUR', max_length=3),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price_currency_at_order',
            field=models.CharField(blank=True, default='EUR', max_length=3),
        ),
    ]

