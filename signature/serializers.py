from django.core.validators import RegexValidator
from .models import Major, Subject, Student
from rest_framework import serializers
import re 

# INFO: In models, the many to many relationship is defined in the Subject model.  So, the SubjectSerializer is defined first.
from django.contrib.auth import get_user_model

User = get_user_model()  # PermissionUser

name_regex = RegexValidator(
        regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
        message="Solo se permiten letras y espacios"
    )
    
    # Validación para RUT (solo números)
rut_regex = RegexValidator(
    regex=r'^\d+$',
    message="El RUT solo debe contener números"
)

# Validación para DV (solo 1 dígito)
dv_regex = RegexValidator(
    regex=r'^[0-9kK]{1}$',  # Considerando posible 'K' como válido para Chile
    message="Digito verificador inválido"
)

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
        password = validated_data.pop('password', None)
        
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
        majors = validated_data.pop('majors', [])
        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            # Con setattr se asigna dinamicamente los atributos (key) en el objeto, eso quiere decir que busca la columna con el nombre key y le asigna el value correspondiente.
            setattr(instance, key, value)

        if password:
            instance.set_password(password)
        
        if majors: 
            instance.majors.set(majors)
        else:
             raise serializers.ValidationError({"majors": "El usuario debe tener asignado por lo menos una carrera."})
        instance.save()
        
        return instance

    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError("El nombre de usuario es obligatorio.")
        
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

class DeleteStudentSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()

    def validate(self, data):
        try:
            student = Student.objects.get(id=data['student_id'])
        except Student.DoesNotExist:
            raise serializers.ValidationError("Estudiante no encontrado")

        self.student = student
        return data

    def save(self):
        self.student.delete()

class CreateStudentSerializer(serializers.Serializer):
    first_name = serializers.CharField(validators=[name_regex])
    second_name = serializers.CharField(
        allow_blank=True,
        required=False,
        validators=[name_regex]
    )
    last_name = serializers.CharField(validators=[name_regex])
    second_last_name = serializers.CharField(
        allow_blank=True,
        required=False,
        validators=[name_regex]
    )
    rut = serializers.CharField(
        validators=[rut_regex],
        max_length=9
    )
    dv = serializers.CharField(
        max_length=1,
        validators=[dv_regex]
    )
    major_id = serializers.IntegerField()

    def validate(self, data):
        # Validación RUT + DV único (mejorada con un solo query)
        if Student.objects.filter(rut=data['rut'], dv=data['dv'].upper()).exists():
            raise serializers.ValidationError("El estudiante ya existe")

        # Validación de existencia de carrera
        try:
            major = Major.objects.get(id=data['major_id'])
        except Major.DoesNotExist:
            raise serializers.ValidationError("Carrera no encontrada")

        # Validación de RUT chileno
        if not self.is_valid_rut(data['rut'], data['dv']):
            raise serializers.ValidationError("El RUT no es válido")

        data['dv'] = data['dv'].upper()
        self.major = major
        return data

    def is_valid_rut(self, rut, dv):
        """
        Valida un RUT chileno según el algoritmo estándar.
        
        Args:
            rut: String con el número de RUT sin puntos ni guión
            dv: String con el dígito verificador (puede ser 'k' o 'K')
        
        Returns:
            Boolean indicando si el RUT es válido
        """
        # Normalizar el dígito verificador
        dv = dv.upper()
        
        # Invertir el RUT para aplicar el algoritmo
        rut_reversed = rut[::-1]
        
        # Aplicar la multiplicación por la secuencia 2,3,4,5,6,7,2,3,...
        factors = [2, 3, 4, 5, 6, 7]
        result = 0
        
        for i, digit in enumerate(rut_reversed):
            result += int(digit) * factors[i % 6]
        
        # Calcular el dígito verificador esperado
        remainder = result % 11
        expected_dv = str(11 - remainder)
        
        # Ajustar casos especiales
        if expected_dv == '11':
            expected_dv = '0'
        elif expected_dv == '10':
            expected_dv = 'K'
        
        # Comparar con el dígito verificador proporcionado
        return expected_dv == dv
    def save(self):
        Student.objects.create(
            first_name=self.validated_data['first_name'],
            second_name=self.validated_data.get('second_name'),
            last_name=self.validated_data['last_name'],
            second_last_name=self.validated_data.get('second_last_name'),
            rut=self.validated_data['rut'],
            dv=self.validated_data['dv'],
            major=self.major
        )


class UpdateStudentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(validators=[name_regex])
    second_name = serializers.CharField(
        allow_blank=True,
        required=False,
        validators=[name_regex]
    )
    last_name = serializers.CharField(validators=[name_regex])
    second_last_name = serializers.CharField(
        allow_blank=True,
        required=False,
        validators=[name_regex]
    )
    rut = serializers.CharField(
        validators=[rut_regex],
        max_length=9
    )
    dv = serializers.CharField(
        max_length=1,
        validators=[dv_regex]
    )
    major_id = serializers.IntegerField()

    def validate_id(self, value):
        if not Student.objects.filter(id=value).exists():
            raise serializers.ValidationError("Estudiante no encontrado.")
        return value

    def validate_rut(self, value):
        student_id = self.initial_data.get('id')
        if Student.objects.filter(rut=value).exclude(id=student_id).exists():
            raise serializers.ValidationError("Ya existe otro estudiante con este RUT.")
        return value

    def validate_dv(self, value):
        # Normalizar DV a mayúsculas
        return value.upper()

    def validate_major_id(self, value):
        try:
            self.major = Major.objects.get(id=value)  # Guardamos en instancia para reutilizar
        except Major.DoesNotExist:
            raise serializers.ValidationError("Carrera no encontrada.")
        return value

    def validate(self, data):
        # Validar que el RUT y DV correspondan a un RUT chileno válido
        if 'rut' in data and 'dv' in data:
            if not self.is_valid_rut(data['rut'], data['dv']):
                raise serializers.ValidationError("El RUT no es válido")
        
        return data

    def is_valid_rut(self, rut, dv):
        """
        Valida un RUT chileno según el algoritmo estándar.
        
        Args:
            rut: String con el número de RUT sin puntos ni guión
            dv: String con el dígito verificador (puede ser 'k' o 'K')
        
        Returns:
            Boolean indicando si el RUT es válido
        """
        # Normalizar el dígito verificador
        dv = dv.upper()
        
        # Invertir el RUT para aplicar el algoritmo
        rut_reversed = rut[::-1]
        
        # Aplicar la multiplicación por la secuencia 2,3,4,5,6,7,2,3,...
        factors = [2, 3, 4, 5, 6, 7]
        result = 0
        
        for i, digit in enumerate(rut_reversed):
            result += int(digit) * factors[i % 6]
        
        # Calcular el dígito verificador esperado
        remainder = result % 11
        expected_dv = str(11 - remainder)
        
        # Ajustar casos especiales
        if expected_dv == '11':
            expected_dv = '0'
        elif expected_dv == '10':
            expected_dv = 'K'
        
        # Comparar con el dígito verificador proporcionado
        return expected_dv == dv
    
    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.second_name = validated_data.get('second_name', instance.second_name)
        instance.last_name = validated_data['last_name']
        instance.second_last_name = validated_data.get('second_last_name', instance.second_last_name)
        instance.rut = validated_data['rut']
        instance.dv = validated_data['dv']
        instance.major = self.major  # Usamos el objeto ya validado
        instance.save()
        return instance

    def save(self):
        # Obtener instancia del estudiante
        instance = Student.objects.get(id=self.validated_data['id'])
        return self.update(instance, self.validated_data)  

class SubjectEnrollmentSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    subject_id = serializers.IntegerField()


    def validate(self, data):
        try:
            student = Student.objects.get(id=data['student_id'])
        except Student.DoesNotExist:
            raise serializers.ValidationError("Estudiante no encontrado")

        try:
            subject = Subject.objects.get(id=data['subject_id'])
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Materia no encontrada")

        if not subject.major.filter(id=student.major.id).exists():
            raise serializers.ValidationError("La materia no pertenece a la carrera del estudiante")

        self.student = student
        self.subject = subject
        return data

    def save(self):
        self.student.subjects.add(self.subject)
        
class UnenrollSubjectSerializer(serializers.Serializer):
    student_ids = serializers.ListField(
        child=serializers.IntegerField()
    )

    subject_id = serializers.IntegerField()

    def validate(self, data):
        try:
            subject = Subject.objects.get(id=data['subject_id'])
            
            # Validate all students
            students = []
            for student_id in data['student_ids']:
                try:
                    student = Student.objects.get(id=student_id)
                    
                    # Check if subject belongs to student's major
                    if not subject.major.filter(id=student.major.id).exists():
                        raise serializers.ValidationError(f"La materia no pertenece a la carrera del estudiante con ID {student_id}")
                    
                    students.append(student)
                except Student.DoesNotExist:
                    raise serializers.ValidationError(f"Estudiante con ID {student_id} no encontrado")
            
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Materia no encontrada")

        self.students = students
        self.subject = subject
        return data
    
    def save(self):
        for student in self.students:
            student.subjects.remove(self.subject)
