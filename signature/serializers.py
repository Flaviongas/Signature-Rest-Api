from rest_framework import serializers
from .models import Major, Subject

# INFO: In models, the many to many relationship is defined in the Subject model.  So, the SubjectSerializer is defined first.


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ('id', 'name', 'major',)


class MajorSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Major
        fields = ('id', 'name', 'faculty', 'subjects',)
