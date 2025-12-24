from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.email


class State(models.Model):
    state_name = models.CharField(max_length=15)

    def __str__(self):
        return self.state_name


class City(models.Model):
    city_name = models.CharField(max_length=15)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.city_name


class Area(models.Model):
    area_name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return self.area_name


class Company(models.Model):
    company_name = models.CharField(max_length=50)
    company_contact = models.CharField(max_length=10)
    company_email = models.EmailField()
    company_address = models.TextField()
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    def __str__(self):
        return self.company_name


class Role(models.Model):
    role_name = models.CharField(max_length=20)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.role_name


class Category(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return self.category_name


class Offer(models.Model):
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.discount_percentage}% OFF"

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    product_description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    stock_quantity = models.IntegerField(default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self.offer:
            self.discount_price = self.price - (self.price * self.offer.discount_percentage / 100)
        else:
            self.discount_price = self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name

class Image(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="product_images/")

    def __str__(self):
        return f"Image for {self.product.product_name}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Cart for {self.user.username}"


class Cart_item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(10)])

    def subtotal(self):
        return self.product.discount_price * self.quantity


class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    house = models.CharField(max_length=100)
    apartment = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('shipping', 'Shipping'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_address = models.ForeignKey(BillingAddress, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def subtotal(self):
        return self.product.price * self.quantity
