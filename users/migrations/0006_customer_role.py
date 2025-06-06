from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_professional_labels_customer_labels'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='role',
            field=models.CharField(
                choices=[
                    ('STANDARD', 'Standard'),
                    ('PREMIUM', 'Premium'),
                    ('VIP', 'VIP'),
                    ('ENTERPRISE', 'Enterprise')
                ],
                default='STANDARD',
                help_text='Customer role - determines access levels and features',
                max_length=20
            ),
        ),
    ]

