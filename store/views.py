from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, Product, Customer, User, OrderItem, ShippingAddress
from django.template import Context, Template
from django.http import JsonResponse
import json
import datetime
from django.contrib import messages
import random
import http.client
from django.views import generic
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password


def store(request):
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        customer = request.user.customer
        print(customer)
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_item': 0, 'shipping': False}
        cartItems = 0

    return render(request, 'store/store.html', context={'products': Product.objects.all(), 'cartItems': cartItems})


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        print(customer)
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        cartItems = 0
        return redirect('login_attampt')
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_item': 0, 'shipping': False}
        cartItems = order['get_cart_item']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print(productId)
    print(action)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()
    messages.success(request, f'item added')
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

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
    return JsonResponse('Payment complete', safe=False)


class Productdetail(generic.DetailView):
    model = Product
    template_name = 'store/product_detail.html'


def product_detail(request, name):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_item': 0, 'shipping': False}
        cartItems = order.get_cart_items
    template_name = 'store/product_detail.html'
    product = get_object_or_404(Product, name=name)
    return render(request, template_name, {'product': product, 'cartItems': cartItems})


def register(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        q = Customer.objects.filter(mobile=mobile).first()
        if not q:
            user = User(username=username, email=email)
            user.save()
            otp = str(random.randint(1000, 9999))
            profile = Customer(user=user, mobile=mobile,
                               otp=otp, email=email, name=username)
            profile.save()
            send_otp(mobile, otp)
            request.session['mobile'] = mobile
            return redirect('otp')
        else:
            context = {
                'success': True,
                'message': 'user is already exist',
                'class': 'alert-danger'
            }
            return render(request, 'store/register.html', context)

    return render(request, 'store/register.html', {'cartItems': 0})


def otp(request):
    mobile = request.session['mobile']
    context = {'mobile': mobile}

    if request.method == 'POST':
        otp = request.POST.get('otp')
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        user = Customer.objects.filter(otp=otp, mobile=mobile).first()
        if user:
            if p1 == p2:
                print(p1, p2, user.name)
                password = make_password(p1)
                p = User.objects.filter(
                    username=user.name).update(password=password)

                return redirect('store')
            else:
                context = {
					'success': True,
                    'message': "enter both the password same",
                    'class': 'alert-danger',
                    'cartItems': 0
				}
                return render(request, 'store/otp.html', context)
        else:
            context = {
				'success': True,
                'message': "enter valid otp",
                'class': 'alert-danger',
                'cartItems': 0
			}
            return render(request, 'store/otp.html',context)
    return render(request, 'store/otp.html', context)


def login_attampt(request):
    context = {'cartItems': 0}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            context = {
                'success': True,
                'message': "invailid username or password",
                'class': 'alert-danger',
                'cartItems': 0
            }
            return render(request, 'store/login.html', context)
    return render(request, 'store/login.html', context)


def forget_password(request):
    context = {'cartItems': 0}
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        verify = Customer.objects.filter(mobile=mobile).first()
        if verify:
            otp = str(random.randint(1000, 9999))
            Customer.objects.filter(mobile=mobile).update(otp=otp)
            send_otp(mobile, otp)
            request.session['mobile'] = mobile
            return redirect('login_otp')
        else:
            context = {
                'success': True,
                'message': "mobile number is not found",
                'class': 'alert-danger',
                'cartItems': 0
            }
            return render(request, 'store/forget_passqord.html', context)
    return render(request, 'store/forget_password.html', context)


def profile(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        print(customer.mobile)
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        if request.method == "POST":
            image = request.POST.get('img')
            print(image)
            customer.image = image
            customer.save()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_item': 0, 'shipping': False}
        cartItems = order.get_cart_items

    return render(request, 'store/profile.html', {'customer': customer, 'cartItems': cartItems})


def login_otp(request):
    mobile = request.session['mobile']
    context = {'mobile': mobile,
               'cartItems': 0}

    if request.method == 'POST':
        otp = request.POST.get('otp')
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        user = Customer.objects.filter(otp=otp, mobile=mobile).first()
        if user:
            if p1 == p2:
                print(p1, p2, user.name)
                password = make_password(p1)
                p = User.objects.filter(
                    username=user.name).update(password=password)

                return redirect('store')
            else:
                context = {
					'success': True,
                    'message': "enter both the password same",
                    'class': 'alert-danger',
                    'cartItems': 0
				}
                return render(request, 'store/otp.html', context)
        else:
            context = {
				'success': True,
                'message': "enter valid otp",
                'class': 'alert-danger',
                'cartItems': 0
			}
            return render(request, 'store/otp.html',context)
    return render(request, 'store/otp.html', context)


def send_otp(mobile, otp):
    print("FUNCTION CALLED")
    conn = http.client.HTTPSConnection("api.msg91.com")
    authkey = settings.AUTH_KEY
    headers = {'content-type': "application/json"}
    url = "http://control.msg91.com/api/sendotp.php?otp="+otp+"&message" + \
        "rambabu%20otp%20is%20"+otp+"&mobile="+mobile+"&authkey="+authkey+"&country=91"
    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data)
    return None


def Type_of_product(request, name):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_item': 0, 'shipping': False}
        cartItems = order.get_cart_items
    products = Product.objects.filter(modeltype=name)
    print(products)
    return render(request, 'store/productType.html', {'products': products, 'cartItems': cartItems})


def log_out(request):
    print('yes')
    print(logout(request))
    print('yes')
    return redirect('cart')
