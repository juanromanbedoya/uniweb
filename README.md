# Uniweb: CRUD de estudiantes (Django + SQLite)

Actividad final de **Programación Integrada Web**.

- **Aplicación en vivo (túnel):** ver el enlace en la página del proyecto: https://juanromanbedoya.github.io/uniweb/
- **Rastro de lo hecho por la IA:** [BITACORA_IA.md](BITACORA_IA.md)

## Qué incluye

1. La lógica del sistema migrada a **SQLite**: modelo `Estudiante` (ORM) y capa de servicio `estudiantes/services.py`.
2. **CRUD** para el registro de personas:

   | Operación | Ruta |
   |---|---|
   | Crear | `/estudiantes/registro/` |
   | Listar / buscar | `/estudiantes/` |
   | Editar | `/estudiantes/editar/<id>/` |
   | Eliminar | `/estudiantes/eliminar/<id>/` |

3. Un **túnel** que da una URL pública hacia el servidor local (`iniciar_tunel.bat`).

## Ejecutar en Windows

```bat
:: Ventana 1: crea el entorno, aplica las migraciones y arranca el servidor
iniciar_servidor.bat

:: Ventana 2: crea la URL pública
iniciar_tunel.bat
```

O manualmente:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Pruebas: `python manage.py test estudiantes` (17 pruebas).

> GitHub Pages solo sirve archivos estáticos. Por eso la carpeta `docs/` es una portada con el enlace a la aplicación, que corre con Django en el equipo del autor y se publica por el túnel.
