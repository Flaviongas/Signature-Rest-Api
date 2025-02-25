from rest_framework import serializers
from .models import Major, Subject


class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    major = MajorSerializer(read_only=True, many=True)

    class Meta:
        model = Subject
        fields = ('id', 'name', 'major',)
