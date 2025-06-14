# Generated by Django 4.2.19 on 2025-04-27 07:36

from django.db import migrations
import json


class Migration(migrations.Migration):

    def RelateStudentsSubjects(apps, schema_editor):
        Student = apps.get_model('signature', 'Student')
        Subject = apps.get_model('signature', 'Subject')
        with open('signature/migrations/students.json', 'r', encoding='utf-8') as file:
            students = json.load(file)
            for student in students:
                found_student = Student.objects.filter(
                    rut=student['Rut'],
                ).first()
                if "Asignatura" in student:
                    found_subject = Subject.objects.filter(
                        name=student['Asignatura']
                    ).first()
                    if found_student and found_subject:
                        found_student.subjects.add(found_subject)
                        found_student.save()

    dependencies = [
        ('signature', '0004_auto_20250427_0725'),
    ]

    operations = [
        migrations.RunPython(
            RelateStudentsSubjects
        ),
    ]
