# Generated by Django 4.2.17 on 2025-02-25 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signature', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='major',
            name='faculty',
            field=models.CharField(default='Sin facultad', max_length=200),
            preserve_default=False,
        ),
    ]
