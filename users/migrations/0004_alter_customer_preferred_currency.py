from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customer_billing_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='preferred_currency',
            field=models.CharField(blank=True, default='EUR', help_text='Preferred currency for pricing', max_length=3),
        ),
    ]

