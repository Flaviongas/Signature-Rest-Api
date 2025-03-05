from rest_framework import serializers
from .models import Major, Subject, Student
from django.contrib.auth.models import User

# INFO: In models, the many to many relationship is defined in the Subject model.  So, the SubjectSerializer is defined first.


class StudentSerializer(serializers.ModelSerializer):
    subjects = serializers.PrimaryKeyRelatedField(many=True,queryset=Subject.objects.all())
    class Meta:
        model = Student
        fields = '__all__'


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


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ('id', 'username', 'password')
