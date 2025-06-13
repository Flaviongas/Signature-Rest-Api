
from django.db import migrations
import json
import os


class Migration(migrations.Migration):
    def insert_majors(apps, schema_editor):
        Major = apps.get_model('signature', 'Major')
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        json_path = os.path.join(base_dir, 'data', 'majors.json')
        with open(json_path, 'r', encoding='utf-8') as file:
            majors = json.load(file)
            for major in majors:
                Major.objects.create(
                    name=major['major'],
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
