from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator, MinValueValidator

from django.core.validators import MaxValueValidator, MinValueValidator


class VotingUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    dni = models.CharField(max_length=9, unique=True, validators=[
        RegexValidator(
            regex='^\d{8}[A-Z]{1}$',
            message='El formato debe ser 8 digitos y una letra mayuscula.'
        )
    ], verbose_name="NIF")

    Sexo_Enum = (
        ('Man', 'Man'),
        ('Woman', 'Woman'),
    )
    sexo = models.CharField(max_length=6, choices=Sexo_Enum, default='Woman', blank=False, verbose_name="Gender")

    Titulo_Enum = (
        ('Software', 'Software'),
        ('Computer Technology', 'Computer Technology'),
        ('Information Technology', 'Information Technology'),
        ('Health', 'Health'),
    )
    titulo = models.CharField(max_length=22, choices=Titulo_Enum, default='Software', blank=False, verbose_name="Grade")

    Curso_Enum = (
        ('First', 'First'),
        ('Second', 'Second'),
        ('Third', 'Third'),
        ('Fourth', 'Fourth'),
        ('Master', 'Master'),
    )

    curso = models.CharField(max_length=7, choices=Curso_Enum, default='First', blank=False, verbose_name="Year")
    
    edad = models.PositiveIntegerField(default=18, blank=False, null=False, validators=[MinValueValidator(17), MaxValueValidator(100)], verbose_name="age")

    def __str__(self):
        return self.user.__str__()