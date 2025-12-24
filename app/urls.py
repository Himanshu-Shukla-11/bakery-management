from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.IndexView, name="index"),
    path("about/", views.AboutView, name="about"),
    path("product/", views.ProductView, name="product"),
    path("contact-us/", views.ContactView, name="contact"),
    path("categories/", views.CategoriesView, name="categories"),
    path("registration/", views.RegistrationView, name="registration"),
    path("login/", views.LoginView, name="login"),
    path("register/", views.UserRegister, name="register"),
    path("loginuser/", views.LoginUser, name="loginuser"),
    path("logoutuser/", views.LoginoutUser, name="logoutuser"),
    path("cart/", views.CartView, name="cart"),
    path("addtocart/<int:pid>/",views.addToCart,name="addtocart"),
    path("removefromcart/<int:cid>/",views.removeFromCart,name="removefromcart"),
    path("updatecart/",views.updateCart,name="updatecart"),
    path("profile/",views.ProfileView,name="profile"),
    path("check-out/", views.CheckOutView, name="check-out"),
    path("placeOrder/", views.placeOrder, name="placeOrder"),
    path("oderdetails/", views.orderDetailsPage, name="orderdetails"),
    path("cancelorder/<int:order_id>/", views.cancelOrder, name="cancel_order"),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)