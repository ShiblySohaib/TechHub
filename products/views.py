from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Category, Product, Review
from django.utils import timezone


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
    now = timezone.now()
    for product in products:
        product.is_new_arrival = (now - product.created_at).days < 7
    context = {
        "category": category,
        "products": products,
    }
    return render(request, "products/category_products.html", context)



def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    user_review_pending_approval = False
    if request.user.is_authenticated and not request.user.is_staff:
        user_pending = product.reviews.filter(user=request.user, is_approved=False).exists()
        user_review_pending_approval = user_pending
        if request.method == 'POST' and not user_pending:
            rating = request.POST.get('rating')
            review_text = request.POST.get('review')
            if rating and review_text:
                Review.objects.create(
                    product=product,
                    user=request.user,
                    rating=rating,
                    review=review_text,
                    is_approved=False
                )
                user_review_pending_approval = True
    context = {
        "product": product,
        "reviews": reviews,
        "user_review_pending_approval": user_review_pending_approval,
    }
    return render(request, "products/product.html", context)