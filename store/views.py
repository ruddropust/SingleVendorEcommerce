import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from django.http import JsonResponse

from .models import Category, Product, Order, OrderItem, OrderStatus
from .forms import RegisterForm, LoginForm, ShippingForm
from .cart import Cart

# Initialize Stripe API Key
stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    """
    Catalog homepage listing all products, with search and category filtering.
    """
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    
    selected_category = None
    category_slug = request.GET.get('category')
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)
        
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(name__icontains=search_query)
        
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
    }
    return render(request, 'store/home.html', context)

def product_detail(request, slug):
    """
    Detailed product page showing product description, image, and stock.
    """
    product = get_object_or_404(Product, slug=slug)
    context = {
        'product': product,
    }
    return render(request, 'store/product_detail.html', context)

def cart_detail(request):
    """
    Shopping cart page showing items, quantities, subtotal, and total.
    """
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

def cart_add(request, product_id):
    """
    Add a product to the shopping cart. Supports standard forms and AJAX.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if not product.is_in_stock:
        if is_ajax:
            return JsonResponse({'success': False, 'message': f"{product.name} is out of stock."})
        messages.error(request, f"{product.name} is currently out of stock.")
        return redirect('store:home')
        
    quantity = int(request.POST.get('quantity', 1))
    override_quantity = request.POST.get('override', 'False') == 'True'
    
    # Check if quantity requested exceeds available stock
    current_in_cart = cart.cart.get(str(product.id), {}).get('quantity', 0)
    requested_total = quantity if override_quantity else current_in_cart + quantity
    
    if requested_total > product.stock:
        if is_ajax:
            return JsonResponse({
                'success': False, 
                'message': f"Only {product.stock} units available. You already have {current_in_cart} in cart."
            })
        messages.warning(request, f"Cannot add requested quantity. Only {product.stock} items left in stock.")
        cart.add(product=product, quantity=product.stock, override_quantity=True)
    else:
        cart.add(product=product, quantity=quantity, override_quantity=override_quantity)
        if is_ajax:
            return JsonResponse({
                'success': True,
                'cart_count': len(cart),
                'message': f"Added {product.name} to your cart."
            })
        messages.success(request, f"Added {product.name} to your cart.")
        
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))

def cart_remove(request, product_id):
    """
    Remove a product from the shopping cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f"Removed {product.name} from your cart.")
    return redirect('store:cart_detail')

def cart_update(request, product_id):
    """
    Update quantity of a product in the shopping cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity <= 0:
                cart.remove(product)
                messages.success(request, f"Removed {product.name} from your cart.")
            elif quantity > product.stock:
                messages.warning(request, f"Cannot update quantity. Only {product.stock} items left in stock.")
                cart.add(product=product, quantity=product.stock, override_quantity=True)
            else:
                cart.add(product=product, quantity=quantity, override_quantity=True)
                messages.success(request, f"Updated quantity for {product.name}.")
        except ValueError:
            messages.error(request, "Invalid quantity provided.")
            
    return redirect('store:cart_detail')

def register(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('store:home')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to our store.")
            return redirect('store:home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('store:home')
        
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Logged in successfully. Welcome back, {user.username}!")
            # Redirect to next URL if present
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('store:home')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('store:home')

@login_required
def checkout(request):
    """
    Checkout page that gathers shipping details and redirects to Stripe Checkout.
    """
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Your cart is empty. Please add products before checking out.")
        return redirect('store:home')
        
    # Double check stock availability before creating order
    for item in cart:
        product = item['product']
        if product.stock < item['quantity']:
            messages.error(request, f"Sorry, {product.name} only has {product.stock} items in stock. Please adjust your cart.")
            return redirect('store:cart_detail')

    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create the order in the database with status 'Pending'
                    order = Order.objects.create(
                        user=request.user,
                        total_amount=cart.get_total_price(),
                        payment_status='Pending',
                        shipping_name=form.cleaned_data.get('shipping_name'),
                        shipping_address=form.cleaned_data.get('shipping_address'),
                        shipping_city=form.cleaned_data.get('shipping_city'),
                        shipping_postal_code=form.cleaned_data.get('shipping_postal_code'),
                        shipping_country=form.cleaned_data.get('shipping_country')
                    )
                    
                    # Create initial order status
                    OrderStatus.objects.create(order=order, status='Order Placed')
                    
                    # Create OrderItem records
                    line_items = []
                    for item in cart:
                        product = item['product']
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            price=item['price'],
                            quantity=item['quantity']
                        )
                        
                        # Add item to Stripe line items list
                        line_items.append({
                            'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                    'name': product.name,
                                    'description': product.description[:100] if product.description else "Product Description",
                                },
                                'unit_amount': int(item['price'] * 100), # Stripe expects unit price in cents
                            },
                            'quantity': item['quantity'],
                        })

                    # Create Stripe Checkout Session
                    success_url = request.build_absolute_uri(reverse('store:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}'
                    cancel_url = request.build_absolute_uri(reverse('store:payment_cancel'))
                    
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=line_items,
                        mode='payment',
                        success_url=success_url,
                        cancel_url=cancel_url,
                        metadata={
                            'order_id': str(order.id),
                        }
                    )
                    
                    # Store session ID on the order
                    order.stripe_session_id = session.id
                    order.save()
                    
                # Redirect to Stripe Checkout page
                return redirect(session.url, code=303)
                
            except stripe.error.StripeError as e:
                messages.error(request, f"Stripe Error: {str(e)}")
            except Exception as e:
                messages.error(request, f"An error occurred during checkout: {str(e)}")
    else:
        # Prepopulate shipping name with user's full name if available
        initial_data = {}
        if request.user.get_full_name():
            initial_data['shipping_name'] = request.user.get_full_name()
        else:
            initial_data['shipping_name'] = request.user.username
            
        form = ShippingForm(initial=initial_data)
        
    return render(request, 'store/checkout.html', {'form': form, 'cart': cart})

@login_required
def payment_success(request):
    """
    Success redirect landing page. Fetches the Stripe Session, verifies payment, 
    reduces stock, marks order as paid, and clears cart.
    """
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, "No checkout session ID was provided.")
        return redirect('store:home')
        
    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        session_data = session.to_dict()
        
        metadata = session_data.get('metadata', {})
        order_id = metadata.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Verify that payment succeeded
        if session_data.get('payment_status') == 'paid':
            # Process stock reduction and payment completion atomically
            if order.payment_status != 'Paid':
                with transaction.atomic():
                    # Double-check and update stock
                    for item in order.items.all():
                        product = item.product
                        # Reduce stock (do not go below 0)
                        if product.stock >= item.quantity:
                            product.stock -= item.quantity
                        else:
                            product.stock = 0
                        product.save()
                        
                    # Update order status
                    order.payment_status = 'Paid'
                    order.save()
                    
                    # Create tracking statuses for paid order
                    OrderStatus.objects.create(order=order, status='Payment')
                    OrderStatus.objects.create(order=order, status='Confirmed')
                    
                    # Clear shopping cart
                    cart = Cart(request)
                    cart.clear()
                    
                messages.success(request, f"Thank you for your purchase! Order #{order.id} has been successfully paid.")
            
            return render(request, 'store/success.html', {'order': order})
        else:
            order.payment_status = 'Failed'
            order.save()
            messages.error(request, "Payment has not been completed. Status: " + str(session_data.get('payment_status')))
            return redirect('store:payment_cancel')
            
    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe verification error: {str(e)}")
        return redirect('store:home')
    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f"An unexpected error occurred during confirmation: {str(e)}")
        return redirect('store:home')

@login_required
def payment_cancel(request):
    """
    Cancel landing page for failed/cancelled payments.
    """
    return render(request, 'store/cancel.html')

@login_required
def order_history(request):
    """
    View user's order history.
    """
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'store/order_history.html', {'orders': orders})

@login_required
def order_track(request, order_id):
    """
    Renders the tracking timeline for a specific order.
    Only the owner of the order or staff/admin can view it.
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Check permissions: owner or staff/admin
    if order.user != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to track this order.")
        return redirect('store:order_history')
        
    # Get all status records for this order, chronologically
    order_statuses = order.statuses.all().order_by('timestamp')
    
    # Sequence of tracking steps
    allowed_steps = [
        "Order Placed", 
        "Processing", 
        "Payment", 
        "Confirmed", 
        "Packing", 
        "Packed", 
        "Delivering", 
        "Delivered"
    ]
    
    # Create a mapping of the statuses that have already occurred
    completed_statuses = {status.status: status for status in order_statuses}
    
    # Find the index of the latest status that has occurred
    latest_index = -1
    for i, step in enumerate(allowed_steps):
        if step in completed_statuses:
            latest_index = i
            
    # Build a timeline list of dicts for the frontend
    timeline = []
    for i, step in enumerate(allowed_steps):
        status_record = completed_statuses.get(step)
        
        if i < latest_index:
            state = 'completed'
            timestamp = status_record.timestamp if status_record else order.order_date
            description = status_record.description if (status_record and status_record.description) else OrderStatus.DEFAULT_DESCRIPTIONS.get(step, '')
        elif i == latest_index:
            state = 'active'
            timestamp = status_record.timestamp if status_record else order.order_date
            description = status_record.description if (status_record and status_record.description) else OrderStatus.DEFAULT_DESCRIPTIONS.get(step, '')
        else:
            state = 'pending'
            timestamp = None
            description = OrderStatus.DEFAULT_DESCRIPTIONS.get(step, '')
            
        timeline.append({
            'status': step,
            'state': state,
            'timestamp': timestamp,
            'description': description
        })
        
    context = {
        'order': order,
        'timeline': timeline,
    }
    return render(request, 'store/order_track.html', context)
