from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Major(models.Model):
    name = models.CharField(max_length=200)
    faculty = models.CharField(max_length=200)

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
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=200)
    major = models.ManyToManyField(Major, related_name='subjects')
    students = models.ManyToManyField(Student, related_name='subjects')

    def __str__(self):
        return self.name


class PermissionUser(AbstractUser):
    majors = models.ManyToManyField(Major, related_name='users')

    def __str__(self):
        return self.username
