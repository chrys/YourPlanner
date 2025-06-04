from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labels', '0001_initial'),
        ('users', '0004_alter_customer_preferred_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='labels',
            field=models.ManyToManyField(blank=True, help_text='Optional labels to categorize this professional', related_name='professionals', to='labels.label'),
        ),
        migrations.AddField(
            model_name='customer',
            name='labels',
            field=models.ManyToManyField(blank=True, help_text='Optional labels to categorize this customer', related_name='customers', to='labels.label'),
        ),
    ]

