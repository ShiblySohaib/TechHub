import datetime
import random

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from sslcommerz_python_api import SSLCSession

from carts.models import Cart, CartProduct
from carts.utils import get_session_key
from products.models import Product

from .models import Order, OrderProduct, Payment



@login_required
def place_order(request):
    if request.user.is_authenticated:
        global global_user 
        global_user = request.user
        cart = get_object_or_404(Cart, user=request.user)
    else:
        cart = get_object_or_404(Cart, session_key=get_session_key())

    cart_products = CartProduct.objects.filter(cart=cart).select_related("product")

    if cart_products.count() == 0:
        return redirect("home")

    quantity = 0
    total = 0
    for cart_product in cart_products:
        total += cart_product.product.price * cart_product.quantity
        quantity += cart_product.quantity

    if request.method == "POST":
        payment_option = request.POST.get("payment_method")

        try:
            current_date = datetime.datetime.now()
            order_number = current_date.strftime("%Y%m%d%H%M%S") + str(random.random())
            current_user = request.user

            order = Order.objects.create(
                user=current_user,
                mobile=getattr(current_user, 'mobile', None) or "+8801234567891",
                address=getattr(current_user, 'address', None) or "N/A",
                country=getattr(current_user, 'country', None) or "N/A",
                postcode=getattr(current_user, 'postcode', None) or "0000",
                city=getattr(current_user, 'city', None) or "N/A",
                order_note=request.POST.get("order_note", ""),
                order_total=total,
                status="Pending",
                order_number=order_number,
            )

            for cart_item in cart_products:
                OrderProduct.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product.price,
                )

                product = Product.objects.get(id=cart_item.product.id)
                


            if payment_option == "cash":
                cart_products.delete()
                if product.stock >= cart_item.quantity:
                    product.stock -= cart_item.quantity
                    product.save()
                order.status = "Completed"
                order.save()
                return render(request, "orders/order-success.html", {"order": order})
            elif payment_option == "sslcommerz":
                return redirect("payment")

        except Exception as e:
            return HttpResponse("Error occurred: " + str(e))

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_products,
        "grand_total": total + settings.DELIVERY_CHARGE,
        "DELIVERY_CHARGE": settings.DELIVERY_CHARGE,
    }

    return render(request, "orders/checkout.html", context=context)


def payment(request):
    mypayment = SSLCSession(
        sslc_is_sandbox=bool(settings.SSLCOMMERZ_IS_SANDBOX),
        sslc_store_id=settings.SSLCOMMERZ_STORE_ID,
        sslc_store_pass=settings.SSLCOMMERZ_STORE_PASS,
    )

    status_url = request.build_absolute_uri("status")

    mypayment.set_urls(
        success_url=status_url,
        fail_url=status_url,
        cancel_url=status_url,
        ipn_url=status_url,
    )

    user = request.user
    order = Order.objects.filter(user=user, status="Pending").last()

    order_products = OrderProduct.objects.filter(order=order).select_related("product")
    if order_products.exists():
        first_product = order_products[0].product
        product_category = getattr(first_product, "category", "general")
        product_name = first_product.name
        num_of_item = sum([op.quantity for op in order_products])
        shipping_method = "YES"
    else:
        product_category = "general"
        product_name = "product"
        num_of_item = 1
        shipping_method = "NO"

    mypayment.set_product_integration(
        total_amount=order.order_total,
        currency="BDT",
        product_category=product_category,
        product_name=product_name,
        num_of_item=num_of_item,
        shipping_method=shipping_method,
        product_profile="None",
    )

    mypayment.set_customer_info(
        name=user.username,
        email=user.email,
        address1=order.address,
        city=order.city,
        postcode=order.postcode,
        country=order.country,
        phone=order.mobile,
    )

    mypayment.set_shipping_info(
        shipping_to=user.first_name,
        address=order.address, 
        city=order.city,
        postcode=order.postcode,
        country=order.country,
    )

    response_data = mypayment.init_payment()
    print(response_data)
    if response_data["status"] == "FAILED":
        order.status = "Failed"
        order.save()

    return redirect(response_data["GatewayPageURL"])


@csrf_exempt
def payment_status(request):
    if request.method == "POST":
        payment_data = request.POST
        if payment_data["status"] == "VALID":
            val_id = payment_data["val_id"]
            tran_id = payment_data["tran_id"]

            order = Order.objects.filter(user=global_user).last()

            payment = Payment.objects.create(
                user=global_user,
                payment_id=val_id,
                payment_method="SSLCommerz",
                amount_paid=order.order_total,
                status="Completed",
            )

            order.status = "Completed"
            order.payment = payment
            order.save()

            order_products = OrderProduct.objects.filter(order=order).select_related("product")
            for order_product in order_products:
                product = order_product.product
                if product.stock >= order_product.quantity:
                    product.stock -= order_product.quantity
                    product.save()

            # CartItems will be automatically deleted
            Cart.objects.filter(user=global_user).delete()

            context = {
                "order": order,
                "transaction_id": tran_id,
            }
            return render(request, "orders/order-success.html", context)

        else:
            return render(request, "orders/order-failed.html")

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user, status="Completed").order_by('-created_at')
    return render(request, "orders/order_history.html", {"orders": orders})
