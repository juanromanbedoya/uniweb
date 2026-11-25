# Bitácora de la IA: actividad final de Uniweb

**Asignatura:** Programación Integrada Web
**Fecha:** 25/11/2026
**Asistente de IA:** Claude Code (modelo Claude Opus 5.5, de Anthropic)
**Guía usada:** presentación de clase *PROGRAMACION INTEGRADA WEB.pptx* (diapositivas 5–52: Django, vistas, ORM, CRUD, capa intermedia, transacciones)

Este archivo registra lo que hizo la IA, en orden, para cumplir los tres puntos de la actividad:

1. Migrar la lógica del sistema para que use un servicio de **SQLite**.
2. Crear el **CRUD** para el registro de las personas.
3. Crear un **túnel** que dé una URL pública para entrar a la aplicación.

---

## 0. Estado inicial (lo que había antes)

- Proyecto Django `uniweb` con la app `estudiantes`.
- Vistas `home`, `saludo` y `registro`. El registro **solo validaba y mostraba** los datos: **no guardaba nada** (no había modelo y `models.py` estaba vacío).
- No había entorno virtual ni base de datos creada.

## 1. Lectura de la guía

La IA extrajo el texto de las 60 diapositivas de la presentación y tomó como referencia:

| Diapositiva | Tema | Cómo se aplicó |
|---|---|---|
| 5 | Entorno virtual `python -m venv venv` | Se creó `venv/` e instaló Django |
| 9 | Herencia de plantillas | Se creó `base.html`; las demás vistas la extienden con `{% extends %}` |
| 22 | SQLite en `settings.py` | Se mantuvo `django.db.backends.sqlite3` y `db.sqlite3` |
| 23 | Modelo `Estudiante (nombre, edad)` | `estudiantes/models.py` |
| 24 | `makemigrations` / `migrate` | Se generó `0001_initial.py` y se creó la tabla |
| 25–30 | Guardar y listar con el ORM | Vistas `registro` y `lista_estudiantes` |
| 37 | Capa intermedia: View → Service → Model → BD | Nuevo archivo `estudiantes/services.py` |
| 38–46 | CRUD: crear, listar, editar, eliminar | Las cuatro operaciones con sus rutas |
| 47–50 | `@transaction.atomic` | Las escrituras del servicio son atómicas |

## 2. Punto 1: migración a SQLite

**Archivos:** `estudiantes/models.py`, `estudiantes/migrations/0001_initial.py`, `uniweb/settings.py`

- Se creó el modelo `Estudiante` con: `nombre` (CharField 100), `edad` (PositiveIntegerField), `fecha_registro` y `fecha_actualizacion` (automáticas).
- Comandos ejecutados:
  ```bash
  python -m venv venv
  venv\Scripts\python -m pip install -r requirements.txt
  venv\Scripts\python manage.py makemigrations estudiantes
  venv\Scripts\python manage.py migrate
  ```
- Resultado: se creó `db.sqlite3` con la tabla `estudiantes_estudiante`.
- **Capa de servicio** (`estudiantes/services.py`): se movió aquí la validación que antes estaba en `views.py` y se agregaron las funciones CRUD. Las vistas ya no usan el ORM directamente.
- El modelo quedó registrado en el panel `/admin/` (`estudiantes/admin.py`).
- En `settings.py` el idioma pasó a `es-co` y la zona horaria a `America/Bogota`.

## 3. Punto 2: CRUD de personas

| Operación | Ruta | Vista | Servicio |
|---|---|---|---|
| **C**reate | `/estudiantes/registro/` | `registro` | `crear_estudiante` |
| **R**ead | `/estudiantes/` (con búsqueda `?q=`) | `lista_estudiantes` | `listar_estudiantes` |
| **U**pdate | `/estudiantes/editar/<id>/` | `editar_estudiante` | `actualizar_estudiante` |
| **D**elete | `/estudiantes/eliminar/<id>/` | `eliminar_estudiante` | `eliminar_estudiante` |

Decisiones que tomó la IA:

- **Validación doble.** JavaScript valida en el navegador antes de enviar (nombre no vacío, edad entera entre 1 y 120) y el servidor repite las mismas reglas en `services.validar_estudiante`.
- **Eliminar se hace con POST y pide confirmación.** La diapositiva 45 lo hace con un enlace GET. La IA prefirió POST para que un enlace o un buscador no puedan borrar registros sin querer.
- **Post/Redirect/Get.** Después de crear, editar o eliminar, la vista redirige a la lista y muestra un mensaje (`django.contrib.messages`). Así, recargar la página no duplica registros.
- **404 si el id no existe** (`get_object_or_404`).
- Un solo formulario (`registro.html`) sirve para crear y para editar.

**Templates:** `base.html` (nuevo), `home.html` (muestra el total de registros), `registro.html`, `lista_estudiantes.html` (nuevo), `eliminar_estudiante.html` (nuevo), `saludo.html`.

## 4. Punto 3: túnel con URL pública

**Archivos:** `uniweb/settings.py`, `iniciar_servidor.bat`, `iniciar_tunel.bat`

- Primero se intentó descargar **Cloudflare Tunnel (`cloudflared`)**, pero el sistema de permisos del asistente bloqueó la descarga del ejecutable.
- Alternativa usada: **localhost.run**, que solo necesita el `ssh` que ya trae Windows:
  ```bash
  ssh -R 80:127.0.0.1:8000 nokey@localhost.run
  ```
- **Problema encontrado:** con `localhost:8000` el túnel respondía **502**, porque `localhost` se resolvía a IPv6 (`::1`) y Django escuchaba en IPv4. **Solución:** usar `127.0.0.1:8000`.
- Para que Django acepte peticiones que llegan por el túnel se agregaron a `settings.py`:
  - `ALLOWED_HOSTS`: dominios `.trycloudflare.com`, `.lhr.life`, `.ngrok-free.app`, `.loca.lt`, entre otros.
  - `CSRF_TRUSTED_ORIGINS`: los mismos dominios con `https://`. Sin esto, los formularios POST enviados desde la URL pública responden 403.
- `iniciar_tunel.bat` usa `cloudflared` si está instalado y, si no, usa localhost.run.

## 5. Verificación

- `python manage.py check`: sin problemas.
- `python manage.py test estudiantes`: **17 pruebas OK**. Cubren crear, listar, buscar, editar, eliminar, validaciones, 404, CSRF y un POST desde un dominio de túnel.
- Prueba manual con `curl` contra el servidor real: crear (302), editar (302) y eliminar (302); el registro quedó en `db.sqlite3` y después se borró.
- Prueba a través del túnel público: `GET /` → 200 y `POST /estudiantes/registro/` → 302, con el registro guardado. Ese registro de prueba también se borró.

## 6. Cómo ejecutar

```bat
:: Ventana 1: servidor
iniciar_servidor.bat

:: Ventana 2: túnel (copiar la URL https que aparece)
iniciar_tunel.bat
```

Rutas locales: `http://127.0.0.1:8000/` · `/estudiantes/` · `/estudiantes/registro/` · `/admin/`

## 7. Estructura final

```
uniweb/
├── BITACORA_IA.md            ← este archivo
├── iniciar_servidor.bat
├── iniciar_tunel.bat
├── manage.py
├── requirements.txt
├── db.sqlite3                ← base de datos SQLite
├── uniweb/
│   ├── settings.py           ← SQLite, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS
│   └── urls.py               ← rutas del CRUD
└── estudiantes/
    ├── models.py             ← modelo Estudiante (ORM)
    ├── services.py           ← capa intermedia: validación + CRUD
    ├── views.py              ← controladores
    ├── admin.py
    ├── tests.py              ← 17 pruebas
    ├── migrations/0001_initial.py
    └── templates/estudiantes/
        ├── base.html
        ├── home.html
        ├── saludo.html
        ├── registro.html             (crear / editar)
        ├── lista_estudiantes.html    (listar / buscar)
        └── eliminar_estudiante.html  (confirmar borrado)
```
