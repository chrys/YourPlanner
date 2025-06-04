from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0002_initial_categories'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='labels',
            field=models.ManyToManyField(blank=True, limit_choices_to={'category__name': 'PROFESSIONAL', 'is_active': True}, related_name='professionals', to='configuration.configurationlabel'),
        ),
        migrations.AddField(
            model_name='customer',
            name='labels',
            field=models.ManyToManyField(blank=True, limit_choices_to={'category__name': 'CUSTOMER', 'is_active': True}, related_name='customers', to='configuration.configurationlabel'),
        ),
    ]

