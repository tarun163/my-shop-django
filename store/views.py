from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.template import Context, Template
from django.http import JsonResponse
import json
import datetime
from django.views import generic

def store(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order,created = Order.objects.get_or_create(customer=customer,complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_item':0,'shipping':False}
		cartItems = order.get_cart_items

	
	return render(request, 'store/store.html', context = {'products':Product.objects.all(),'cartItems':cartItems})


def cart(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order,created = Order.objects.get_or_create(customer=customer,complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_item':0,'shipping':False}
		cartItems = order.get_cart_items
	context = {'items':items,'order':order,'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order,created = Order.objects.get_or_create(customer=customer,complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_item':0,'shipping':False}
		cartItems = order.get_cart_items
	context = {'items':items,'order':order,'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']

	print(productId)
	print(action)
	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order,created = Order.objects.get_or_create(customer=customer,complete=False)

	orderItem,created = OrderItem.objects.get_or_create(order=order,product=product) 

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()
	if orderItem.quantity<=0:
		orderItem.delete()
  
	return JsonResponse('item was added',safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order,created = Order.objects.get_or_create(customer=customer,complete=False)
       
		order.transaction_id = transaction_id

		if float(data['form']['total']) == order.get_cart_total:
			order.complete = True
		order.save()	

		if order.shipping == True:
			ShippingAddress.objects.create(
				customer=customer,
				order=order,
				address=data['shipping']['address'],
				city=data['shipping']['city'],
				state=data['shipping']['state'],
				zipcode=data['shipping']['zipcode'],
			)

	else:
		print('user is not logged in')		
	return JsonResponse('Payment complete',safe=False)


class Productdetail(generic.DetailView):
	model = Product
	template_name = 'store/product_detail.html'

def product_detail(request,name):
	template_name = 'store/product_detail.html'
	product = get_object_or_404(Product,name=name)
	return render(request, template_name,{'product':product})

