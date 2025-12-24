from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import *


# ---------------- HOME ----------------

def IndexView(request):
    return render(request, "app/index.html")


def AboutView(request):
    return render(request, "app/about.html")


def ProductView(request):
    return render(request, "app/product.html")


def ContactView(request):
    return render(request, "app/contact.html")


def CategoriesView(request):
    category_filter = request.GET.get("f")

    if category_filter:
        products = Product.objects.filter(
            category__category_name__iexact=category_filter
        )
    else:
        products = Product.objects.all()

    return render(request, "app/categories.html", {
        "all_product": products,
        "selected_category": category_filter
    })


def RegistrationView(request):
    return render(request, "app/registration.html")


def LoginView(request):
    return render(request, "app/login.html")


# ---------------- REGISTER ----------------

def UserRegister(request):
    if request.method == "POST":
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"].lower().strip()
        contact = request.POST["contact"]
        password = request.POST["password"]
        cpassword = request.POST["cpassword"]

        if password != cpassword:
            return render(request, "app/registration.html", {"msg": "Passwords do not match"})

        if User.objects.filter(username=email).exists():
            return render(request, "app/registration.html", {"msg": "User already exists"})

        user = User.objects.create_user(
            username=email,
            password=password,
            first_name=fname,
            last_name=lname
        )

        UserProfile.objects.create(
            user=user,
            email=email,
            contact=contact
        )

        Cart.objects.create(user=user)
        return redirect("login")

    return render(request, "app/registration.html")


# ---------------- LOGIN ----------------

def LoginUser(request):
    if request.method == "POST":
        email = request.POST["email"].lower().strip()
        password = request.POST["password"]

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect("index")

        return render(request, "app/login.html", {"msg": "Invalid email or password"})

    return render(request, "app/login.html")


def LoginoutUser(request):
    logout(request)
    return redirect("index")


# ---------------- CART ----------------

@login_required
def CartView(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "app/cart.html", {
        "cart": cart,
        "cart_items": cart.items.all()
    })

@login_required
def addToCart(request, pid):
    product = get_object_or_404(Product, id=pid)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    qty = int(request.GET.get("qty", 1))

    if product.stock_quantity < qty:
        messages.error(request, "Out of stock")
        return redirect("categories")

    cart_item, created = Cart_item.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 0}   # ✅ IMPORTANT
    )

    # If item already exists, check stock
    if not created:
        if cart_item.quantity + qty > product.stock_quantity:
            messages.error(request, "Only limited stock available")
            return redirect("cart")

    # Increase quantity only ONCE
    cart_item.quantity += qty
    cart_item.save()

    cart.total_price = sum(i.subtotal() for i in cart.items.all())
    cart.save()

    return redirect("cart")


@login_required
def removeFromCart(request, cid):
    cart_item = get_object_or_404(Cart_item, id=cid, cart__user=request.user)
    cart = cart_item.cart
    cart_item.delete()

    cart.total_price = sum(i.subtotal() for i in cart.items.all())
    cart.save()

    return redirect("cart")


@login_required
def updateCart(request):
    if request.method == "POST":
        cart = Cart.objects.get(user=request.user)

        for item in cart.items.all():
            qty = int(request.POST.get(f"cartQty{item.id}", item.quantity))
            # cap quantity to available stock
            if qty > item.product.stock_quantity:
                messages.error(
                    request,
                    f"Only {item.product.stock_quantity} item(s) available for {item.product.product_name}"
                )
                qty = item.product.stock_quantity

            item.quantity = max(1, qty)
            item.save()

        cart.total_price = sum(i.subtotal() for i in cart.items.all())
        cart.save()

    return redirect("cart")


# ---------------- PROFILE ----------------

@login_required
def ProfileView(request):
    return render(request, "app/profile.html", {
        "profile": request.user.profile
    })


# ---------------- CHECKOUT ----------------

@login_required
def CheckOutView(request):
    cart = Cart.objects.get(user=request.user)
    if not cart.items.exists():
        return redirect("cart")

    return render(request, "app/check-out.html", {
        "cart_items": cart.items.all(),
        "total": cart.total_price
    })


# ---------------- PLACE ORDER ----------------

@login_required
@transaction.atomic
def placeOrder(request):
    if request.method != "POST":
        return redirect("cart")

    cart = Cart.objects.get(user=request.user)
    items = cart.items.select_for_update()

    if not items.exists():
        return redirect("cart")

    billing = BillingAddress.objects.create(
        user=request.user,
        house=request.POST["house"],
        apartment=request.POST["apartment"],
        city=request.POST["city"],
        state=request.POST["state"],
        pincode=request.POST["pincode"]
    )

    order = Order.objects.create(
        user=request.user,
        billing_address=billing,
        total_price=cart.total_price
    )

    for item in items:
        if item.product.stock_quantity < item.quantity:
            messages.error(request, "Insufficient stock")
            return redirect("cart")

        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity
        )

        item.product.stock_quantity -= item.quantity
        item.product.save()

    items.delete()
    cart.total_price = 0
    cart.save()

    return redirect("orderdetails")


# ---------------- ORDERS ----------------

@login_required
def orderDetailsPage(request):
    orders = request.user.orders.all().order_by("-created_at")
    return render(request, "app/order-details.html", {"orders": orders})


@login_required
def cancelOrder(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Allow cancel ONLY if order is pending
    if order.status != "pending":
        return redirect("orderdetails")

    # Restore product stock
    for item in order.items.all():
        product = item.product
        product.stock_quantity += item.quantity
        product.save()

    # Update order status
    order.status = "cancelled"
    order.save()

    return redirect("orderdetails")

