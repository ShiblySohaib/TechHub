from django.db import models
from django.utils.text import slugify

from accounts.models import CustomUser


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class Category(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="categories")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.name}"
    



class Product(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    is_avaiable = models.BooleanField(default=True)
    unit = models.CharField(max_length=50)
    image = models.ImageField(upload_to="products")
    category = models.ForeignKey(
        Category, null=True, related_name = "products", on_delete=models.SET_NULL
    )
    is_featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.name}"
    
    def average_approved_rating(self):
        approved_reviews = self.reviews.filter(is_approved=True)
        if approved_reviews.exists():
            return round(approved_reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return None
    


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/images")

    def __str__(self):
        return f"Image for {self.product.name}"



class Review(TimeStampedModel):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        CustomUser, related_name="reviews", on_delete=models.CASCADE
    )

    rating = models.FloatField()
    review = models.TextField()

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.is_approved} - Review by {self.user.first_name} for {self.product.name}"
