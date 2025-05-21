from django.shortcuts import redirect, render
from .models import Category, Product


def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True)
    context = {
        "categories": categories,
        "featured_products": featured_products,
    }
    return render(request, "products/home.html", context)


def category_view(request, slug):
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter(category=category)
    context = {
        "category": category,
        "products": products,
    }
    return render(request, "products/category.html", context)