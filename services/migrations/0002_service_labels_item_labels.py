from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0002_initial_categories'),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='labels',
            field=models.ManyToManyField(blank=True, limit_choices_to={'category__name': 'SERVICE', 'is_active': True}, related_name='services', to='configuration.configurationlabel'),
        ),
        migrations.AddField(
            model_name='item',
            name='labels',
            field=models.ManyToManyField(blank=True, limit_choices_to={'category__name': 'SERVICE', 'is_active': True}, related_name='items', to='configuration.configurationlabel'),
        ),
    ]

