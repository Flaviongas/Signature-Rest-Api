from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

# Create your models here.


class MajorCode(models.Model):
    # Las carreras tienen más de un código por alguna razón, culpen a la U
    code = models.CharField(max_length=15)
    major = models.ForeignKey(
        'Major',
        on_delete=models.CASCADE,
        related_name='codes',
        null=True,
    )

    def __str__(self):
        return self.code


class Major(models.Model):
    name = models.CharField(max_length=50)
    faculty = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Student(models.Model):
    rut = models.CharField(max_length=20)
    dv = models.CharField(max_length=1)
    first_name = models.CharField(max_length=200)
    second_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    second_last_name = models.CharField(max_length=200)
    major = models.ForeignKey(Major, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name}"


class Subject(models.Model):
    name = models.CharField(max_length=200)
    major = models.ForeignKey(
        Major, on_delete=models.CASCADE, related_name='subjects', null=True)
    students = models.ManyToManyField(Student, related_name='subjects')

    def __str__(self):
        return self.name


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con las carreras asignadas
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Crear el superusuario sin asignar majors por ahora
        user = self.create_user(username, email, password, **extra_fields)

        # Asignar todas las carreras después de crear el usuario
        all_majors = Major.objects.all()
        user.majors.set(all_majors)

        return user


class PermissionUser(AbstractUser):
    majors = models.ManyToManyField(Major, related_name='users')

    objects = CustomUserManager()

    def __str__(self):
        return self.username
