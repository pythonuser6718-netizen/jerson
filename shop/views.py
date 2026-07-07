from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Product, Category, Brand, Order, OrderItem
from .cart import Cart
from .forms import CheckoutForm, SignUpForm


def home(request):
    featured = Product.objects.filter(is_active=True, is_featured=True)[:8]
    latest = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {
        'featured': featured,
        'latest': latest,
        'categories': categories,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    brands = Brand.objects.all()

    category_slug = request.GET.get('category')
    brand_id = request.GET.get('brand')
    query = request.GET.get('q')
    sort = request.GET.get('sort')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_id:
        products = products.filter(brand__id=brand_id)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(brand__name__icontains=query)
        )
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'query': query or '',
        'selected_category': category_slug or '',
        'selected_brand': brand_id or '',
        'sort': sort or '',
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    return render(request, 'shop/product_detail.html', {'product': product, 'related': related})


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart_detail.html', {'cart': cart})


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    messages.success(request, f'"{product.name}" added to your cart.')
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f'"{product.name}" removed from your cart.')
    return redirect('cart_detail')


def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity <= 0:
        cart.remove(product)
    else:
        cart.add(product=product, quantity=quantity, override_quantity=True)
    return redirect('cart_detail')


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('product_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
                item['product'].stock = max(0, item['product'].stock - item['quantity'])
                item['product'].save()
            cart.clear()
            messages.success(request, f"Order #{order.id} placed successfully! We'll contact you shortly.")
            return redirect('order_success', order_id=order.id)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {'full_name': request.user.get_full_name(), 'email': request.user.email}
        form = CheckoutForm(initial=initial)

    return render(request, 'shop/checkout.html', {'form': form, 'cart': cart})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/order_success.html', {'order': order})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome.")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
