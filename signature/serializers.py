from rest_framework import serializers
from .models import Major, Subject, Student
import re 

# INFO: In models, the many to many relationship is defined in the Subject model.  So, the SubjectSerializer is defined first.
from django.contrib.auth import get_user_model

User = get_user_model()  # PermissionUser


class StudentSerializer(serializers.ModelSerializer):
    subjects = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Subject.objects.all())

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
    password = serializers.CharField(write_only=True, required=False)
    major_ids = serializers.PrimaryKeyRelatedField(
        source='majors',
        queryset=Major.objects.all(),   # Usamos el modelo de Major
        many=True,                      # Puede ser una lista de IDs
        write_only=True,                # Este campo es solo para escritura
        required=False                  # No es obligatorio en el POST si no quieres asociar carreras al principio
    )
    majors = MajorSerializer(many=True, read_only=True) 
    
    class Meta(object):
        model = User
        fields = ('id', 'username', 'password', 'majors', 'major_ids', 'is_superuser')
    
    def create(self, validated_data):
        majors = validated_data.pop('majors', [])
        print(majors)
        password = validated_data.pop('password')
        
        if not password:
            raise serializers.ValidationError({"password": "La contraseña es obligatoria."})
        
        if not majors:
            raise serializers.ValidationError({"majors": "El usuario debe tener asignado por lo menos una carrera."})
        
        user = User(**validated_data)
        user.is_superuser = False
        user.is_staff = False  
        user.set_password(password)
        user.save()
        
        if majors:
            user.majors.set(majors) 
        
        return user
    
    def update(self, instance, validated_data):
        majors = validated_data.pop('majors', None)
        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            # Con setattr se asigna dinamicamente los atributos (key) en el objeto, eso quiere decir que busca la columna con el nombre key y le asigna el value correspondiente.
            setattr(instance, key, value)

        if password:
            instance.set_password(password)
        
        if majors is not None: 
            instance.majors.set(majors)

        instance.save()
        
        return instance

    def validate_username(self, value):
        if not value:
            raise ValidationError("El nombre de usuario es obligatorio.")
        
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError("El nombre de usuario solo puede contener letras y números.")
        
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
        
        return value
