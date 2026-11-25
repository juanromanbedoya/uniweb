from django.db import models


class Estudiante(models.Model):
    """Tabla de personas registradas (ORM: Tabla -> Clase, Fila -> Objeto).

    Se guarda en SQLite (uniweb/settings.py -> DATABASES).
    """

    nombre = models.CharField(max_length=100)
    edad = models.PositiveIntegerField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_registro", "-id"]
        verbose_name = "estudiante"
        verbose_name_plural = "estudiantes"

    def __str__(self):
        return self.nombre
