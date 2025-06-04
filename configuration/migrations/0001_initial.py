from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigurationCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(choices=[('WEBSITE', 'Website'), ('PROFESSIONAL', 'Professional'), ('SERVICE', 'Services and Items'), ('CUSTOMER', 'Customer')], max_length=50, unique=True)),
                ('description', models.TextField(blank=True, help_text='Description of this configuration category', null=True)),
            ],
            options={
                'verbose_name': 'Configuration Category',
                'verbose_name_plural': 'Configuration Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ConfigurationLabel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, help_text='Explanation of this label', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labels', to='configuration.configurationcategory')),
            ],
            options={
                'verbose_name': 'Configuration Label',
                'verbose_name_plural': 'Configuration Labels',
                'ordering': ['category', 'name'],
            },
        ),
        migrations.AddConstraint(
            model_name='configurationlabel',
            constraint=models.UniqueConstraint(fields=('category', 'name'), name='unique_category_label'),
        ),
    ]

