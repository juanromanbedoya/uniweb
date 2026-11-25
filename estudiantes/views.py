from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from . import services


def saludo(request):
    """Primer endpoint de la clase (/saludo/). Su respuesta viaja por la vista HTML."""
    return render(request, "estudiantes/saludo.html", {"mensaje": "Hola desde el servidor (Django)"})


def home(request):
    """Vista principal (/). La view envía datos al template y este renderiza el HTML."""
    contexto = {
        "titulo": "Home Estudiantes",
        "total": services.listar_estudiantes().count(),
    }
    return render(request, "estudiantes/home.html", contexto)


# ------------------------------------------------------------------ CRUD

def lista_estudiantes(request):
    """READ (/estudiantes/): tabla con los registros guardados en SQLite."""
    busqueda = request.GET.get("q", "").strip()
    contexto = {
        "titulo": "Lista de Estudiantes",
        "estudiantes": services.listar_estudiantes(busqueda),
        "busqueda": busqueda,
    }
    return render(request, "estudiantes/lista_estudiantes.html", contexto)


@require_http_methods(["GET", "POST"])
def registro(request):
    """CREATE (/estudiantes/registro/).

    GET  -> muestra el formulario vacío.
    POST -> valida en el servidor; si todo está bien guarda en SQLite y redirige a la lista.
    """
    contexto = {"titulo": "Registro de Estudiantes", "boton": "Guardar"}

    if request.method == "POST":
        nombre, edad = services.limpiar_datos(request.POST)
        errores = services.validar_estudiante(nombre, edad)
        if not errores:
            estudiante = services.crear_estudiante(nombre, edad)
            messages.success(request, f"Registro guardado: {estudiante.nombre}, {estudiante.edad} años.")
            return redirect("lista_estudiantes")
        contexto["errores"] = errores
        contexto["valores"] = {"nombre": nombre, "edad": edad}

    return render(request, "estudiantes/registro.html", contexto)


@require_http_methods(["GET", "POST"])
def editar_estudiante(request, id):
    """UPDATE (/estudiantes/editar/<id>/): mismo formulario, precargado con el registro."""
    estudiante = services.obtener_estudiante(id)
    contexto = {
        "titulo": "Editar Estudiante",
        "boton": "Actualizar",
        "estudiante": estudiante,
        "valores": {"nombre": estudiante.nombre, "edad": estudiante.edad},
    }

    if request.method == "POST":
        nombre, edad = services.limpiar_datos(request.POST)
        errores = services.validar_estudiante(nombre, edad)
        if not errores:
            services.actualizar_estudiante(estudiante, nombre, edad)
            messages.success(request, f"Registro actualizado: {estudiante.nombre}, {estudiante.edad} años.")
            return redirect("lista_estudiantes")
        contexto["errores"] = errores
        contexto["valores"] = {"nombre": nombre, "edad": edad}

    return render(request, "estudiantes/registro.html", contexto)


@require_http_methods(["GET", "POST"])
def eliminar_estudiante(request, id):
    """DELETE (/estudiantes/eliminar/<id>/).

    GET  -> pide confirmación.
    POST -> borra el registro (borrar con POST evita eliminaciones por un simple enlace).
    """
    estudiante = services.obtener_estudiante(id)

    if request.method == "POST":
        nombre = estudiante.nombre
        services.eliminar_estudiante(estudiante)
        messages.success(request, f"Registro eliminado: {nombre}.")
        return redirect("lista_estudiantes")

    return render(
        request,
        "estudiantes/eliminar_estudiante.html",
        {"titulo": "Eliminar Estudiante", "estudiante": estudiante},
    )
