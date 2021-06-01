from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, null = True,blank=True, on_delete=models.CASCADE)
    name = models.CharField(null=True, max_length=50)
    email = models.CharField(null=True, max_length=50)
    image = models.ImageField(null=True,blank=True)
    otp = models.CharField( max_length=50,null=True,blank=True) 
    mobile = models.CharField(max_length=50,null=True,blank=True)

    def __str__(self):
        return self.name or 'tarun'

class Product(models.Model):
    name = models.CharField(null=True, max_length=50) 
    price = models.FloatField()
    productDetail = models.TextField(null=True,blank=True)
    degital = models.BooleanField(default=False,null=True,blank=False)
    image = models.ImageField(null=True,blank=True)
    def __str__(self):
        return self.name or ''

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url            

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True,null=True)
    date_order = models.DateTimeField( auto_now_add=True)
    complete =  models.BooleanField(default=False,null=True,blank=False)
    transaction_id = models.CharField( max_length=200,null=True)
 
    def __str__(self):
        return self.transaction_id or ''

    @property 
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.degital == False:
                shipping = True
            return shipping    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total 

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total        

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True,null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True,null=True)
    quantity = models.IntegerField(default=0, null=True,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True,null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True,null=True)
    address = models.CharField(null=True, max_length=200)
    city = models.CharField(null=True, max_length=200)
    state = models.CharField(null=True, max_length=200)
    zipcode = models.CharField(null=True, max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer or ''