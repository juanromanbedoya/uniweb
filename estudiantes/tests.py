import re

from django.test import Client, TestCase
from django.urls import reverse

from .models import Estudiante


class VistasBasicasTests(TestCase):
    def test_home_usa_su_template_y_muestra_el_total(self):
        Estudiante.objects.create(nombre="Ana", edad=20)
        respuesta = self.client.get(reverse("home"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "estudiantes/home.html")
        self.assertContains(respuesta, "Home Estudiantes")
        self.assertContains(respuesta, 'data-url="/estudiantes/registro/"')
        self.assertContains(respuesta, "<strong>1</strong>")

    def test_saludo_responde_a_traves_del_template(self):
        respuesta = self.client.get(reverse("saludo"))
        self.assertTemplateUsed(respuesta, "estudiantes/saludo.html")
        self.assertContains(respuesta, "Hola desde el servidor (Django)")


class CrearTests(TestCase):
    def test_get_muestra_el_formulario(self):
        respuesta = self.client.get(reverse("registro"))
        self.assertTemplateUsed(respuesta, "estudiantes/registro.html")
        self.assertContains(respuesta, 'name="nombre"')
        self.assertContains(respuesta, 'name="edad"')
        self.assertContains(respuesta, ">Guardar</button>")

    def test_post_valido_guarda_en_sqlite_y_redirige_a_la_lista(self):
        respuesta = self.client.post(reverse("registro"), {"nombre": "  Ana Pérez ", "edad": "20"}, follow=True)
        self.assertRedirects(respuesta, reverse("lista_estudiantes"))
        estudiante = Estudiante.objects.get()
        self.assertEqual((estudiante.nombre, estudiante.edad), ("Ana Pérez", 20))
        self.assertContains(respuesta, "Registro guardado: Ana Pérez, 20 años.")

    def test_post_invalido_muestra_errores_y_no_guarda(self):
        casos = [
            ("nombre", {"nombre": "", "edad": "20"}, "El nombre no puede estar vacío."),
            ("nombre", {"nombre": "   ", "edad": "20"}, "El nombre no puede estar vacío."),
            ("nombre", {"nombre": "a" * 101, "edad": "20"}, "El nombre no puede tener más de 100 caracteres."),
            ("edad", {"nombre": "Ana", "edad": ""}, "La edad es obligatoria."),
            ("edad", {"nombre": "Ana", "edad": "abc"}, "La edad debe ser un número."),
            ("edad", {"nombre": "Ana", "edad": "0"}, "La edad debe ser mayor que 0."),
            ("edad", {"nombre": "Ana", "edad": "-5"}, "La edad debe ser mayor que 0."),
            ("edad", {"nombre": "Ana", "edad": "20.5"}, "La edad debe ser un número entero."),
            ("edad", {"nombre": "Ana", "edad": "121"}, "La edad no puede ser mayor que 120."),
        ]
        for campo, datos, mensaje in casos:
            with self.subTest(datos=datos):
                respuesta = self.client.post(reverse("registro"), datos)
                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, f'id="error-{campo}" role="alert">{mensaje}</small>')
        self.assertEqual(Estudiante.objects.count(), 0)

    def test_post_funciona_con_la_proteccion_csrf_activa(self):
        cliente = Client(enforce_csrf_checks=True)
        pagina = cliente.get(reverse("registro")).content.decode()
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', pagina).group(1)

        con_token = cliente.post(reverse("registro"), {"nombre": "Luis", "edad": "30", "csrfmiddlewaretoken": token})
        self.assertEqual(con_token.status_code, 302)

        sin_token = cliente.post(reverse("registro"), {"nombre": "Luis", "edad": "30"})
        self.assertEqual(sin_token.status_code, 403)
        self.assertEqual(Estudiante.objects.count(), 1)

    def test_post_desde_el_dominio_del_tunel_es_aceptado(self):
        cliente = Client(enforce_csrf_checks=True)
        host = "demo-uniweb.trycloudflare.com"
        pagina = cliente.get(reverse("registro"), HTTP_HOST=host).content.decode()
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', pagina).group(1)
        respuesta = cliente.post(
            reverse("registro"),
            {"nombre": "Remoto", "edad": "25", "csrfmiddlewaretoken": token},
            HTTP_HOST=host,
            HTTP_ORIGIN=f"https://{host}",
            secure=True,
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Estudiante.objects.filter(nombre="Remoto").exists())


class LeerTests(TestCase):
    def test_lista_vacia(self):
        respuesta = self.client.get(reverse("lista_estudiantes"))
        self.assertTemplateUsed(respuesta, "estudiantes/lista_estudiantes.html")
        self.assertContains(respuesta, "No hay estudiantes registrados.")

    def test_lista_muestra_los_registros_con_sus_acciones(self):
        ana = Estudiante.objects.create(nombre="Ana", edad=20)
        Estudiante.objects.create(nombre="Luis", edad=1)
        respuesta = self.client.get(reverse("lista_estudiantes"))
        self.assertContains(respuesta, "Ana")
        self.assertContains(respuesta, "20 años")
        self.assertContains(respuesta, "1 año<")
        self.assertContains(respuesta, reverse("editar_estudiante", args=[ana.id]))
        self.assertContains(respuesta, reverse("eliminar_estudiante", args=[ana.id]))

    def test_busqueda_por_nombre(self):
        Estudiante.objects.create(nombre="Ana", edad=20)
        Estudiante.objects.create(nombre="Luis", edad=30)
        respuesta = self.client.get(reverse("lista_estudiantes"), {"q": "lu"})
        self.assertContains(respuesta, "Luis")
        self.assertNotContains(respuesta, "<td>Ana</td>")


class ActualizarTests(TestCase):
    def setUp(self):
        self.estudiante = Estudiante.objects.create(nombre="Ana", edad=20)
        self.url = reverse("editar_estudiante", args=[self.estudiante.id])

    def test_get_precarga_el_formulario(self):
        respuesta = self.client.get(self.url)
        self.assertContains(respuesta, 'value="Ana"')
        self.assertContains(respuesta, 'value="20"')
        self.assertContains(respuesta, ">Actualizar</button>")

    def test_post_valido_actualiza(self):
        respuesta = self.client.post(self.url, {"nombre": "Ana María", "edad": "21"})
        self.assertRedirects(respuesta, reverse("lista_estudiantes"))
        self.estudiante.refresh_from_db()
        self.assertEqual((self.estudiante.nombre, self.estudiante.edad), ("Ana María", 21))

    def test_post_invalido_no_actualiza(self):
        respuesta = self.client.post(self.url, {"nombre": "", "edad": "21"})
        self.assertContains(respuesta, "El nombre no puede estar vacío.")
        self.estudiante.refresh_from_db()
        self.assertEqual(self.estudiante.nombre, "Ana")

    def test_id_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse("editar_estudiante", args=[999])).status_code, 404)


class EliminarTests(TestCase):
    def setUp(self):
        self.estudiante = Estudiante.objects.create(nombre="Ana", edad=20)
        self.url = reverse("eliminar_estudiante", args=[self.estudiante.id])

    def test_get_pide_confirmacion_y_no_borra(self):
        respuesta = self.client.get(self.url)
        self.assertContains(respuesta, "¿Seguro que quieres eliminar")
        self.assertTrue(Estudiante.objects.exists())

    def test_post_borra_el_registro(self):
        respuesta = self.client.post(self.url, follow=True)
        self.assertRedirects(respuesta, reverse("lista_estudiantes"))
        self.assertContains(respuesta, "Registro eliminado: Ana.")
        self.assertFalse(Estudiante.objects.exists())

    def test_id_inexistente_da_404(self):
        self.assertEqual(self.client.post(reverse("eliminar_estudiante", args=[999])).status_code, 404)
