from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labels', '0001_initial'),
        ('services', '0008_alter_servicecategory_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='labels',
            field=models.ManyToManyField(blank=True, help_text='Optional labels to categorize this service', related_name='services', to='labels.label'),
        ),
        migrations.AddField(
            model_name='item',
            name='labels',
            field=models.ManyToManyField(blank=True, help_text='Optional labels to categorize this item', related_name='items', to='labels.label'),
        ),
        migrations.AddField(
            model_name='price',
            name='labels',
            field=models.ManyToManyField(blank=True, help_text='Optional labels to categorize this price', related_name='prices', to='labels.label'),
        ),
    ]

