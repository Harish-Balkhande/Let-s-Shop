from django.shortcuts import render,redirect
from django.views import View
from .models import Cart, Product, OrderPlaced, Customer
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
# for function based view
from django.contrib.auth.decorators import login_required
# For class based view
from django.utils.decorators import method_decorator

# Home page
class ProductView(View):
    def get(self, request):
        topwares = Product.objects.filter(category='TW')
        bottomwares = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='m')
        laptops = Product.objects.filter(category='L')          
        context = {'topwares':topwares, 'bottomwares':bottomwares, 'mobiles':mobiles, 'Laptops':laptops}
        return render(request, "app/home.html", context)

def cart_badge(request):
    if request.user.is_authenticated:
            cart_items = [p for p in Cart.objects.all() if p.user == request.user]  
            cart_length = len(cart_items)  
            print("cart : ",cart_length) 
            data = {
                'badge':cart_length
            }
            return JsonResponse(data)


# Prduct detail page (add-to-cart & buy now options)
class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            # Checks if item is already in cart to prevent same product to be added in the cart.
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request,'app/productdetail.html', {'product':product, 'item_already_in_cart':item_already_in_cart})

# ------------------------------Cart --------------------------------------

# Add product in the cart
@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect('/cart/')

# Shows product added in the cart by the user if any
@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        # Returns queryset
        cart = Cart.objects.filter(user=user)
        # print(cart)
        amount = 0.0
        shipping_amt = 70.0
        total_amt = 0.0
        # list comprihension used(returns list of objects)
        # Retrives all object of cart and compairs wit current user & return if match
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        # print(cart_product)
        if cart_product:
            for p in cart_product:
                temp_amt = (p.quantity * p.product.discounted_price)
                amount += temp_amt
                total_amt = amount + shipping_amt
            return render(request, 'app/addtocart.html', {'carts':cart, 'total':total_amt, 'product_price':amount})
        else:
            return render(request, 'app/emptycart.html')

# increase product quantity and calculate in cart
def plus_cart(request):
    if request.method == "GET":
        # ID of the product inside cart
        prod_id = request.GET['prod_id']
        # matchs 'poduct'(cart model field) with "cart product_id" and 'registered user' with 'current user' if product availabel and user is the valid user extrat that user object.  
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amt = 70.0
        total_amt = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                temp_amt = (p.quantity * p.product.discounted_price)
                amount += temp_amt                
            data = {
                'quantity':c.quantity,
                'amount':amount, 
                'total':amount + shipping_amt
            }
            return JsonResponse(data)

# Decrease product quantity and calculate amount in cart
def minus_cart(request):
    if request.method == "GET":
        # ID of the product inside cart
        prod_id = request.GET['prod_id']          
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))        
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amt = 70.0
        total_amt = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                temp_amt = (p.quantity * p.product.discounted_price)
                amount += temp_amt
                
            data = {
                'quantity':c.quantity,
                'amount':amount, 
                'total':amount + shipping_amt
            }
            return JsonResponse(data)

# Delete product from cart on 'Remove' button press
def remove_item_in_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']   
        # print("product id: ",prod_id)       
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))    
        # print("cart object",c)
        c.delete()        
        amount = 0.0
        shipping_amt = 70.0
        # total_amt = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        # print("cart product :",cart_product)        
        for p in cart_product:
            temp_amt = (p.quantity * p.product.discounted_price)
            amount += temp_amt            
        data = {            
            'amount':amount, 
            'total':amount + shipping_amt
        }
        return JsonResponse(data)



def buy_now(request):
 return render(request, 'app/buynow.html')

# -------------------------Profile ---------------------------------------------

# Registration, Login, logOut, password change, password reset is done using Django provided Template view in urls.py

# User profile registration form
@method_decorator(login_required, name="dispatch")
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

# shows address in profile
@login_required
def address(request):
    addr = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'address':addr, 'active':'btn-primary'})

# Resgister new customer
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

# -------------------------- Filter --------------------------------------

# filter mobiles from product model
def mobile(request, data=None):
    print(data)
    if data==None:
        mobiles = Product.objects.filter(category='m')
    elif data == 'Realme' or  data == 'Lava':
        mobiles = Product.objects.filter(brand=data)
    return render(request, 'app/mobile.html', {'mobiles':mobiles})

# ------------------------- Order placing --------------------------------

# Procced order for payment
@login_required
def checkout(request):
    user = request.user    
    addr = Customer.objects.filter(user=user)    
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amt = 70.0
    total_amt = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            temp_amt = (p.quantity * p.product.discounted_price)
            amount += temp_amt   
        total_amt = amount + shipping_amt     
        return render(request, 'app/checkout.html', {'address':addr, 'total':total_amt,'cart_items':cart_items})

# On placing the order delete the item in cart and saves the detail into 'orders'
@login_required
def payment_done(request):
    user = request.user
    # we need customer id of checkout order, which is available at submit button value attribute.We can extract it by its name i.e. 'custid'
    cust_id = request.GET.get('custid')
    customer = Customer.objects.get(id=cust_id)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Save to OrderPlaced database
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        # Deleting place order from cart
        c.delete()
    return redirect("orders")

# Shows placed orders
@login_required
def orders(request):
    ord_placed = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'orders':ord_placed})

