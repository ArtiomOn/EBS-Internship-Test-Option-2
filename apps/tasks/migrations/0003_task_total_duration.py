# Generated by Django 3.2.4 on 2021-06-28 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_delete_timer'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='total_duration',
            field=models.DurationField(null=True),
        ),
    ]
