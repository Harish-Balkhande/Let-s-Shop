from django.shortcuts import render
from django.views import View
from .models import Cart, Product, OrderPlaced, Customer
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages

class ProductView(View):
    def get(self, request):
        topwares = Product.objects.filter(category='TW')
        bottomwares = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='m')
        laptops = Product.objects.filter(category='L')
        context = {'topwares':topwares, 'bottomwares':bottomwares, 'mobiles':mobiles, 'Laptops':laptops}
        return render(request, "app/home.html", context)

class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request,'app/productdetail.html', {'product':product})

def add_to_cart(request):
 return render(request, 'app/addtocart.html')

def buy_now(request):
 return render(request, 'app/buynow.html')

class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request,"app/profile.html",{'form':form, 'active':'btn-primary'})
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request, "congratulations! Profile Updated Successfully...")
            form = CustomerProfileForm()
            return render(request, "app/profile.html", {'form':form, 'active':'btn-primary'})


def address(request):
    addr = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'address':addr, 'active':'btn-primary'})

def orders(request):
 return render(request, 'app/orders.html')

def mobile(request, data=None):
    print(data)
    if data==None:
        mobiles = Product.objects.filter(category='m')
    elif data == 'Realme' or  data == 'Lava':
        mobiles = Product.objects.filter(brand=data)
    return render(request, 'app/mobile.html', {'mobiles':mobiles})

class CustomerRegisterationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request,"app/customerregistration.html",{'form':form})
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,"Registered Successfullly!")
            form.save()
            form = CustomerRegistrationForm()
        return render(request,"app/customerregistration.html",{'form':form})


def checkout(request):
 return render(request, 'app/checkout.html')
