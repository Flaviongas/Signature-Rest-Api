from rest_framework import serializers
from .models import Major, Subject, Student

# INFO: In models, the many to many relationship is defined in the Subject model.  So, the SubjectSerializer is defined first.


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id', 'rut', 'dv', 'first_name', 'second_name',
                  'last_name', 'second_last_name',)


class SubjectSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ('id', 'name', 'major', 'students',)


class MajorSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Major
        fields = ('id', 'name', 'faculty', 'subjects',)
