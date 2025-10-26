from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):  # New migration for Agent

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(  # Add Agent model
            name='Agent',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='agent_profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('title', models.CharField(blank=True, help_text='Agent title or role (e.g., Support Agent, Sales Agent)', max_length=200, null=True)),
                ('bio', models.TextField(blank=True, help_text='Brief bio or description of the agent', null=True)),
                ('department', models.CharField(blank=True, help_text='Department or team the agent belongs to', max_length=200, null=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('SUSPENDED', 'Suspended')], default='ACTIVE', help_text='Current status of the agent', max_length=20)),
                ('profile_image', models.ImageField(blank=True, help_text='Agent profile photo', null=True, upload_to='agent_profiles/')),
                ('contact_phone', models.CharField(blank=True, help_text='Agent contact phone number', max_length=20, null=True)),
                ('notes', models.TextField(blank=True, help_text='Internal notes about this agent', null=True)),
                ('labels', models.ManyToManyField(blank=True, help_text='Optional labels to categorize this agent', related_name='agents', to='labels.label')),
            ],
            options={
                'verbose_name': 'Agent',
                'verbose_name_plural': 'Agents',
            },
        ),
        migrations.AddIndex(  # Add database indexes
            model_name='agent',
            index=models.Index(fields=['status'], name='users_agent_status_idx'),
        ),
        migrations.AddIndex(
            model_name='agent',
            index=models.Index(fields=['department'], name='users_agent_department_idx'),
        ),
    ]