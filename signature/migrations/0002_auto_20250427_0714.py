
from django.db import migrations
import json


class Migration(migrations.Migration):
    def insert_majors(apps, schema_editor):
        Major = apps.get_model('signature', 'Major')
        with open('signature/migrations/majors.json', 'r') as file:
            majors = json.load(file)
            for major in majors:
                Major.objects.create(
                    name=major['name'],
                    faculty=major['faculty'],
                )

    dependencies = [
        ('signature', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            insert_majors
        ),
    ]
