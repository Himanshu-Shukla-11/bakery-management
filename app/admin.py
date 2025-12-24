from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from .models import (
    UserProfile, State, City, Area, Company, Role,
    Offer, Category, Product, Image,
    Cart, Cart_item, Order, OrderItem, BillingAddress
)

# ---------------- PDF EXPORT ACTION ---------------- #

def download_pdf(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=report.pdf'

    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("GULSHAN BAKERY & SWEETS", styles['Title']))
    elements.append(Spacer(1, 20))

    data = [[field.name for field in modeladmin.model._meta.fields]]

    for obj in queryset:
        data.append([str(getattr(obj, field.name)) for field in modeladmin.model._meta.fields])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    elements.append(table)
    doc.build(elements)
    return response

download_pdf.short_description = "Download selected as PDF"


# ---------------- USER ADMIN ---------------- #

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email")


# ---------------- USER PROFILE ---------------- #

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "contact")
    search_fields = ("email", "first_name", "last_name")


# ---------------- PRODUCT ADMIN ---------------- #

class ImageInline(admin.StackedInline):
    model = Image
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = ("product_name", "category", "price", "discount_price", "stock_quantity")
    readonly_fields = ("discount_price",)



# ---------------- READ-ONLY BASE ---------------- #

class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------- CART ADMIN ---------------- #

@admin.register(Cart)
class CartAdmin(ReadOnlyAdmin):
    list_display = ("user",)


@admin.register(Cart_item)
class CartItemAdmin(ReadOnlyAdmin):
    list_display = ("cart", "product", "quantity")


# ---------------- ORDER ADMIN ---------------- #

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "total_price", "status", "created_at")
    list_editable = ("status",)
    actions = [download_pdf]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity")


# ---------------- OTHER MODELS ---------------- #

admin.site.register(State)
admin.site.register(City)
admin.site.register(Area)
admin.site.register(Company)
admin.site.register(Role)
admin.site.register(Offer)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(BillingAddress)
