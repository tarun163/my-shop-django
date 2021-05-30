from django.urls import path

from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('profile/', views.profile, name="profile"),
	path('login/', views.login, name="login"),
	path('', views.logout, name="logout"),
	path('register/', views.register, name="register"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('update_Item/', views.updateItem, name="update_Item"),
	path('process_Order/', views.processOrder, name="process_Order"),
	path('<slug:name>/', views.product_detail, name="product_detail"),
	
]