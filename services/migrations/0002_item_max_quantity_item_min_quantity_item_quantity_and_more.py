# Generated by Django 5.1.11 on 2025-06-14 09:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='max_quantity',
            field=models.IntegerField(blank=True, help_text='Maximum quantity per order.', null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='item',
            name='min_quantity',
            field=models.IntegerField(blank=True, help_text='Minimum quantity per order.', null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='item',
            name='quantity',
            field=models.IntegerField(default=0, help_text='Available quantity, cannot be negative.', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='service',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='service_images/'),
        ),
        migrations.AddField(
            model_name='service',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
