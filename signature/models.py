from django.db import models

# Create your models here.


class Major(models.Model):
    name = models.CharField(max_length=200)
    faculty = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=200)
    major = models.ManyToManyField(Major)

    def __str__(self):
        return self.name

# class Student(models.Model):
#     name = models.CharField(max_length=200)
#     email = models.EmailField()
#     document = models.CharField(max_length=20)
#     phone = models.CharField(max_length=20)
#     registration = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.name
