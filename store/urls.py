from django.urls import path

from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('register/', views.register, name="register"),
	path('profile/', views.profile, name="profile"),
	path('login_otp/', views.login_otp, name='login_otp'),
	path('login/', views.login_attampt, name="login_attampt"),
	path('', views.logout, name="logout"),
	path('otp/', views.otp, name='otp'),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('update_Item/', views.updateItem, name="update_Item"),
	path('process_Order/', views.processOrder, name="process_Order"),
	path('<slug:name>/', views.product_detail, name="product_detail"),
	
]