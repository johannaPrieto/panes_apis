from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    TIPO_CHOICES = [
        ('dulce', 'Dulce'),
        ('salado', 'Salado'),
    ]
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    ingredientes = models.TextField()
    instrucciones = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    imagen = models.ImageField(upload_to='recipes/', blank=True, null=True)
    zona = models.CharField(max_length=100, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titulo