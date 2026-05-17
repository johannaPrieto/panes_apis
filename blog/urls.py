from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
   path('', views.publicaciones, name='publicaciones'),
   path('recipe/<int:id>/', views.recipe_detail, name='recipe_detail'),
   path('recipe/<int:id>/edit/', views.editar_recipe, name='editar_recipe'),
   path('crear/', views.crear_recipe, name='crear_recipe'),

   path('recipe/<int:id>/delete/', views.delete_recipe, name='delete_recipe'),

   # AUTH
   path('login/', views.custom_login, name='login'),
   path('logout/', views.custom_logout, name='logout'),

   # API
   path('api/recipes/', views.api_recipes, name='api_recipes'),
   path('api/recipes/<int:id>/', views.api_recipe_detail, name='api_recipe_detail'),
   path('api/js', views.api_json, name='json_api'),

   path('comments/', include('django_comments_xtd.urls')),
]