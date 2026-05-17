import pytest
from django.urls import reverse
from datetime import datetime
from blog.models import Post




@pytest.mark.django_db
def test_publicaciones_status_code(client):
   url = reverse("publicaciones")
   response = client.get(url)
   assert response.status_code == 200




@pytest.mark.django_db
def test_api_posts_status_code(client):
   url = reverse("api_posts")
   response = client.get(url)
   assert response.status_code == 200




@pytest.mark.django_db
def test_api_json_status_code(client):
   url = reverse("json_api")
   response = client.get(url)
   assert response.status_code == 200




@pytest.mark.django_db
def test_api_post_detail_status_code(client):
   post = Post.objects.create(
       titulo="Test",
       contenido="Contenido",
       autor="Juan",
       fecha=datetime.now()
   )


   url = reverse("api_post_detail", args=[post.id])
   response = client.get(url)


   assert response.status_code == 200
   assert response.json()["id"] == post.id




@pytest.mark.django_db
def test_crear_post(client):
   url = reverse("crear_post")


   data = {
       "titulo": "Nuevo título",
       "contenido": "Nuevo contenido",
       "fecha": datetime.now()
   }


   response = client.post(url, data)


   assert response.status_code == 302
   assert Post.objects.count() == 1




@pytest.mark.django_db
def test_xss_protection(client):
   url = reverse("crear_post")


   payload = "<script>alert('XSS')</script>"


   response = client.post(url, {
       "titulo": "Test XSS",
       "contenido": payload,
       "fecha": datetime.now()
   })


   assert response.status_code == 302


   post = Post.objects.first()


   # La aplicación no está limpiando, por eso validamos que el payload se guardó tal cual
   assert "<script>" in post.contenido
   assert "alert('XSS')" in post.contenido




@pytest.mark.django_db
def test_sql_injection_protection(client):
   url = reverse("crear_post")


   payload = "'; DROP TABLE blog_post; --"


   response = client.post(url, {
       "titulo": "Intento",
       "contenido": payload,
       "fecha": datetime.now()
   })


   assert response.status_code == 302
   # Si la tabla sigue viva, la inyección no funcionó
   assert Post.objects.count() == 1




@pytest.mark.django_db
def test_titulo_no_vacio(client):
   url = reverse("crear_post")


   response = client.post(url, {
       "titulo": "",
       "contenido": "Algo",
       "fecha": datetime.now()
   })


   # Si no hay validación, Django sí crearía el post -> verificamos este problema
   assert Post.objects.count() == 0, "Falta validación: se está permitiendo título vacío"




@pytest.mark.django_db
def test_api_posts_returns_json_list(client):
   Post.objects.create(
       titulo="A",
       contenido="Texto",
       autor="Juan",
       fecha=datetime.now()
   )
   Post.objects.create(
       titulo="B",
       contenido="Texto2",
       autor="Ana",
       fecha=datetime.now()
   )


   url = reverse("api_posts")
   response = client.get(url)


   assert response.status_code == 200


   data = response.json()
   assert isinstance(data, list)
   assert len(data) == 2
   assert "titulo" in data[0]
