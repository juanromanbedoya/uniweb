"""Capa intermedia (lógica de negocio): View -> Service -> Model -> BD.

Aquí se validan los datos y se hacen las operaciones CRUD contra SQLite.
Las vistas no tocan el ORM directamente y el HTML no contiene reglas de negocio.
"""

import re

from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Estudiante

# Número con formato simple (20, -5, 20.5...). Es la misma regla que usa el
# JavaScript del formulario.
PATRON_NUMERO = re.compile(r"-?[0-9]+(\.[0-9]+)?")
MAX_NOMBRE = 100
MAX_EDAD = 120


def validar_estudiante(nombre, edad):
    """Devuelve un diccionario {campo: mensaje} con los errores (vacío si todo está bien).

    Son las mismas reglas del JavaScript del formulario: el navegador valida para
    responder rápido, pero el servidor siempre vuelve a validar.
    """
    errores = {}

    if nombre == "":
        errores["nombre"] = "El nombre no puede estar vacío."
    elif len(nombre) > MAX_NOMBRE:
        errores["nombre"] = f"El nombre no puede tener más de {MAX_NOMBRE} caracteres."

    if edad == "":
        errores["edad"] = "La edad es obligatoria."
    elif not PATRON_NUMERO.fullmatch(edad):
        errores["edad"] = "La edad debe ser un número."
    elif float(edad) <= 0:
        errores["edad"] = "La edad debe ser mayor que 0."
    elif not float(edad).is_integer():
        errores["edad"] = "La edad debe ser un número entero."
    elif float(edad) > MAX_EDAD:
        errores["edad"] = f"La edad no puede ser mayor que {MAX_EDAD}."

    return errores


def limpiar_datos(datos):
    """Toma nombre y edad de un request.POST y les quita los espacios sobrantes."""
    return datos.get("nombre", "").strip(), datos.get("edad", "").strip()


# ---------------------------------------------------------------- CRUD

def listar_estudiantes(busqueda=""):
    """READ: todos los registros (o los que coinciden con la búsqueda por nombre)."""
    estudiantes = Estudiante.objects.all()
    if busqueda:
        estudiantes = estudiantes.filter(nombre__icontains=busqueda)
    return estudiantes


def obtener_estudiante(id):
    """READ de un solo registro; responde 404 si no existe."""
    return get_object_or_404(Estudiante, id=id)


@transaction.atomic
def crear_estudiante(nombre, edad):
    """CREATE: inserta una fila nueva en SQLite."""
    return Estudiante.objects.create(nombre=nombre, edad=int(float(edad)))


@transaction.atomic
def actualizar_estudiante(estudiante, nombre, edad):
    """UPDATE: modifica la fila existente."""
    estudiante.nombre = nombre
    estudiante.edad = int(float(edad))
    estudiante.save()
    return estudiante


@transaction.atomic
def eliminar_estudiante(estudiante):
    """DELETE: borra la fila de la base de datos."""
    estudiante.delete()
