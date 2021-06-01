from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.template import Context, Template
from django.http import JsonResponse
import json
import datetime
import random
import http.client
from django.views import generic
from django.conf import settings

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
		return redirect('login_attampt')
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
		cartItems = order['get_cart_item']
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
	if request.user.is_authenticated:
		customer = request.user.customer
		order,created = Order.objects.get_or_create(customer=customer,complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_item':0,'shipping':False}
		cartItems = order.get_cart_items
	template_name = 'store/product_detail.html'
	product = get_object_or_404(Product,name=name)
	return render(request, template_name,{'product':product,'cartItems':cartItems})

	

def register(request):
   
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        q = Customer.objects.filter(mobile = mobile).first()
        if not q:
            user = User(username = username,email=email)
            user.save()
            otp = str(random.randint(1000,9999))
            profile = Customer(user = user,mobile=mobile,otp=otp,email=email,name=username)
            profile.save()
            send_otp(mobile,otp)
            request.session['mobile'] = mobile
            return redirect('otp')
        else:
            context = {
                'success':True,
                'messege':'user is already exist',
                'class':'alert-danger'
            }
            return render(request,'store/register.html',context)
                
    return render(request,'store/register.html')        

def login_attampt(request):

    if request.method == 'POST':
         mobile = request.POST.get('mobile')
         verify = Customer.objects.filter(mobile = mobile).first()
         if not verify:
             context = {
                 'success':True,
                 'messege':'user is not found ',
                 'class':'alert-danger'
             }
             return render(request,'login.html',context)
         otp = str(random.randint(1000,9999))
         verify.otp = otp
         verify.save()
         send_otp(mobile,otp)
         request.session['mobile'] = mobile
         return redirect('login_otp')
  
    return render(request,'store/login.html',{'cartItems':0})

def logout(request):
	return render(request,'store/store.html')

def profile(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		print(customer.mobile)
		order,created = Order.objects.get_or_create(customer=customer,complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
		if request.method == "POST":
			image = request.FILES.get('img')
			print(image)
			customer.image = image
	else: 
		items = []
		order = {'get_cart_total':0, 'get_cart_item':0,'shipping':False}
		cartItems = order.get_cart_items

    		
	return render(request,'store/profile.html',{'customer':customer,'cartItems':cartItems})

def otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        verify = Customer.objects.filter(otp = otp ).first()
        
        #print(Customer.mobile)
        if verify:
            context = {
                'success':True,
                'messege':'Welcome',
                'class':'alert-success'
            }
            return render(request,'store/store.html',context)         

    return render(request,'store/otp.html',)  

def login_otp(request):
    mobile = request.session['mobile']

    context = {'mobile':mobile}
    if request.method == 'POST':
        otp = request.POST.get('otp')
		
        verify = Customer.objects.filter(otp = otp,mobile=mobile).first()
        print(mobile)
        print(otp)
        if verify is not None:		    
            context = {
                'success':True,
                'messege':'Welcome',
                'class':'alert-success'
            }
            return render(request,'store/store.html',context)    
    return render(request,'store/login_otp.html',context)  

def send_otp(mobile,otp):
    print("FUNCTION CALLED")
    conn = http.client.HTTPSConnection("api.msg91.com")
    authkey = settings.AUTH_KEY 
    headers = { 'content-type': "application/json" }
    url = "http://control.msg91.com/api/sendotp.php?otp="+otp+"&message"+"rambabu%20otp%20is%20"+otp+"&mobile="+mobile+"&authkey="+authkey+"&country=91"
    conn.request("GET", url , headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data)
    return None

def Type_of_product(request,name):
	print(name)
	product = Product.objects.filter(modeltype=name)
	return render(request,'store/productType.html',{'product':product,'cartItems':0})
