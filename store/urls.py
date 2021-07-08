from django.urls import path

from . import views

urlpatterns = [
    # Leave as empty string for base url
    path('', views.store, name="store"),
    path('log_out/', views.log_out, name="log_out"),
    path('forget_password/', views.forget_password, name="forget_password"),
    path('product/<slug:name>/', views.Type_of_product, name="Type_of_product"),
    path('register/', views.register, name="register"),
    path('profile/', views.profile, name="profile"),
    path('login_otp/', views.login_otp, name='login_otp'),
    path('login/', views.login_attampt, name="login_attampt"),
    path('otp/', views.otp, name='otp'),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_Item/', views.updateItem, name="update_Item"),
    path('process_Order/', views.processOrder, name="process_Order"),
    path('<slug:name>/', views.product_detail, name="product_detail"),

]
