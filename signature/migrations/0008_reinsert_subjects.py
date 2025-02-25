
from django.db import migrations
import json
from signature.models import Subject, Major


class Migration(migrations.Migration):
    def InsertSubjects(models, schema_editor):
        f = open('subjects.json')
        data = json.load(f)

        for subject in data:
            majors = subject.get('major')
            for unique_major in majors:
                found_major = Major.objects.get(name=unique_major)
                if found_major:
                    added_subject, created = Subject.objects.get_or_create(name=subject.get(
                        'name'))
                    added_subject.major.add(found_major)
                else:
                    print(f"Major {unique_major} not found")

        # Closing file
        f.close()

    dependencies = [
        ('signature', '0007_delete_subjects'),
    ]
    operations = [
        migrations.RunPython(InsertSubjects),
    ]
