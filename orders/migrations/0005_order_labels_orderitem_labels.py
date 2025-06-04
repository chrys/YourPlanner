from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labels', '0001_initial'),
        ('orders', '0004_alter_order_currency_alter_orderitem_price_currency_at_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='labels',
            field=models.ManyToManyField(blank=True, help_text='Optional labels to categorize this order', related_name='orders', to='labels.label'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='labels',
            field=models.ManyToManyField(blank=True, help_text='Optional labels to categorize this order item', related_name='order_items', to='labels.label'),
        ),
    ]

