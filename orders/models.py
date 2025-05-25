from django.db import models

from accounts.models import CustomUser
from products.models import Product, TimeStampedModel


class Payment(TimeStampedModel):
    user = models.ForeignKey(
        CustomUser, null=True, related_name="payments", on_delete=models.SET_NULL
    )
    payment_id = models.CharField(null=True, blank=True, max_length=255)
    payment_method = models.CharField(null=True, blank=True, max_length=255)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(null=True, max_length=255)


class Order(TimeStampedModel):
    user = models.ForeignKey(
        CustomUser, null=True, related_name="orders", on_delete=models.SET_NULL
    )
    payment = models.ForeignKey(Payment, null=True, on_delete=models.CASCADE)

    order_number = models.CharField(max_length=255, null=True, blank=True)
    order_note = models.CharField(max_length=255, null=True, blank=True)

    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)

    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(null=True, max_length=255)

    def __str__(self):
        return f"Order {self.status} - {self.order_number} - {self.user.email if self.user else 'Guest'}"


class OrderProduct(TimeStampedModel):
    order = models.ForeignKey(
        Order, related_name="order_products", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="order_products", on_delete=models.CASCADE
    )
    quantity = models.IntegerField(default=0)

    product_price = models.DecimalField(max_digits=10, decimal_places=2)
