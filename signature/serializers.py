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
    password = serializers.CharField(write_only=True)
    
    class Meta(object):
        model = User
        fields = ('id', 'username', 'password')
    
    def create(self, validated_data):
                
        password = validated_data.pop('password')
        
        user = User.objects.create(**validated_data)
        
        user.set_password(password)
        
        user.save()
        
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            # Con setattr se asigna dinamicamente los atributos (key) en el objeto, eso quiere decir que busca la columna con el nombre key y le asigna el value correspondiente.
            setattr(instance, key, value)

        if password:
            instance.set_password(password)

        instance.save()
        
        return instance

    def validate_username(self, value):
        if not value:
            raise ValidationError("El nombre de usuario es obligatorio.")
        
        if not value.isalpha():
            raise serializers.ValidationError("El nombre de usuario solo puede contener letras.")
        
        return value
    
    def validate_password(self, value):
        # Solo se verificara cuando la password sea distinta de None, osea cuando el usuario cambio la contraseña
        if value is None:
            return value
        
        # # Longitud mínima
        # if len(value) < 8:
        #     raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        # # Requiere al menos un número
        # if not re.search(r'\d', value):
        #     raise serializers.ValidationError("La contraseña debe contener al menos un número.")
        
        # # Requiere al menos una letra mayúscula
        # if not re.search(r'[A-Z]', value):
        #     raise serializers.ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        # return value