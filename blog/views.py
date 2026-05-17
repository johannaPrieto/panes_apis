from django.shortcuts import render, redirect
from .models import Recipe, Category #importar el modelo
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required



def publicaciones(request):
   recipes = Recipe.objects.all().order_by('-fecha')
   return render(request, 'blog/publicaciones.html', {'recipes': recipes})

from django.shortcuts import render, redirect
from .models import Recipe

@login_required
def crear_recipe(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        ingredientes = request.POST.get("ingredientes", "").strip()
        instrucciones = request.POST.get("instrucciones", "").strip()
        tipo = request.POST.get("tipo")
        imagen = request.FILES.get("imagen")
        categoria_id = request.POST.get("categoria")
        zona = request.POST.get("zona", "").strip()

        # Validación simple
        if not titulo or not descripcion or not ingredientes or not instrucciones or not tipo:
            return render(request, "blog/crear.html", {
                "error": "Todos los campos son obligatorios",
                "titulo": titulo,
                "descripcion": descripcion,
                "ingredientes": ingredientes,
                "instrucciones": instrucciones,
                "tipo": tipo,
            })

        # Creación del registro
        recipe_kwargs = dict(
            titulo=titulo,
            descripcion=descripcion,
            ingredientes=ingredientes,
            instrucciones=instrucciones,
            tipo=tipo,
            autor=request.user,
            categoria_id=categoria_id if categoria_id else None,
            zona=zona,
        )
        if imagen:
            recipe_kwargs['imagen'] = imagen

        try:
            Recipe.objects.create(**recipe_kwargs)
        except Exception as e:
            # Si falla la subida (ej. Cloudinary no configurado), reintentar sin imagen
            if 'imagen' in recipe_kwargs:
                recipe_kwargs.pop('imagen')
                Recipe.objects.create(**recipe_kwargs)
            else:
                raise
        return redirect("publicaciones")

    # Si es GET, simplemente mostramos el formulario
    categories = Category.objects.all()
    return render(request, "blog/crear.html", {"categories": categories})

def api_recipes(request):
    recipes = Recipe.objects.all().values('id', 'titulo', 'descripcion', 'ingredientes', 'instrucciones', 'tipo', 'imagen', 'fecha', 'autor__username', 'categoria__name')
    return JsonResponse(list(recipes), safe=False)

from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    return render(request, 'blog/recipe_detail.html', {'recipe': recipe})

def api_recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    data = {
        'id': recipe.id,
        'titulo': recipe.titulo,
        'descripcion': recipe.descripcion,
        'ingredientes': recipe.ingredientes,
        'instrucciones': recipe.instrucciones,
        'tipo': recipe.tipo,
        'imagen': recipe.imagen.url if recipe.imagen else None,
        'fecha': recipe.fecha,
        'autor': recipe.autor.username,
        'categoria': recipe.categoria.name if recipe.categoria else None,
    }
    return JsonResponse(data)

def api_json(request):
    return render(request, 'blog/api.html')
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

@login_required
def editar_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if recipe.autor != request.user and not request.user.is_superuser:
        return HttpResponseForbidden('No tienes permiso para editar esta receta')

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        ingredientes = request.POST.get('ingredientes', '').strip()
        instrucciones = request.POST.get('instrucciones', '').strip()
        tipo = request.POST.get('tipo')
        imagen = request.FILES.get('imagen')
        categoria_id = request.POST.get('categoria')
        zona = request.POST.get('zona', '').strip()

        if not titulo or not descripcion or not ingredientes or not instrucciones or not tipo:
            categories = Category.objects.all()
            return render(request, 'blog/crear.html', {
                'recipe': recipe,
                'categories': categories,
                'error': 'Todos los campos son obligatorios',
            })

        recipe.titulo = titulo
        recipe.descripcion = descripcion
        recipe.ingredientes = ingredientes
        recipe.instrucciones = instrucciones
        recipe.tipo = tipo
        recipe.categoria_id = categoria_id if categoria_id else None
        recipe.zona = zona
        if imagen:
            recipe.imagen = imagen
        recipe.save()
        return redirect('recipe_detail', id=recipe.id)

    categories = Category.objects.all()
    return render(request, 'blog/crear.html', {
        'recipe': recipe,
        'categories': categories,
        'edit_mode': True,
    })


def custom_login(request):
    next_url = request.POST.get('next') or request.GET.get('next') or ''
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect("publicaciones")
        else:
            return render(request, "registration/login.html", {
                "form": form,
                "error": "Usuario o contraseña incorrectos",
                "next": next_url,
            })

    form = AuthenticationForm(request)
    return render(request, "registration/login.html", {"form": form, "next": next_url})


@login_required
def delete_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        # Only author or superuser can delete
        if recipe.autor == request.user or request.user.is_superuser:
            recipe.delete()
            return redirect('publicaciones')
        return HttpResponseForbidden('No tienes permiso para eliminar esta receta')

    # For GET, redirect to detail
    return redirect('recipe_detail', id=id)

