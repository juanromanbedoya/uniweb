"""
Rutas del proyecto uniweb.

Aquí se "exponen" las URLs: cada path apunta a una vista (función) de
estudiantes/views.py, y la vista decide qué template HTML se devuelve.
"""

from django.contrib import admin
from django.urls import path

from estudiantes.views import (
    editar_estudiante,
    eliminar_estudiante,
    home,
    lista_estudiantes,
    registro,
    saludo,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("saludo/", saludo, name="saludo"),
    # CRUD de estudiantes (SQLite)
    path("estudiantes/", lista_estudiantes, name="lista_estudiantes"),
    path("estudiantes/registro/", registro, name="registro"),
    path("estudiantes/editar/<int:id>/", editar_estudiante, name="editar_estudiante"),
    path("estudiantes/eliminar/<int:id>/", eliminar_estudiante, name="eliminar_estudiante"),
]
