from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_servicecategory_alter_item_options_item_position_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='currency',
            field=models.CharField(blank=True, default='EUR', max_length=3),
        ),
    ]

