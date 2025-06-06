# Generated by Django 5.1.10 on 2025-06-05 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labels', '0002_label_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='label',
            name='type',
            field=models.CharField(choices=[('general', 'General'), ('priority', 'Priority'), ('status', 'Status'), ('custom', 'Custom'), ('professional', 'Professional Tag'), ('customer', 'Customer Tag'), ('service', 'Service Tag'), ('item', 'Item Tag'), ('price', 'Price Tag'), ('order', 'Order Tag')], default='general', max_length=20),
        ),
    ]
