import json
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Cake, Order


# -------------------------------------------------------------
# CART HELPER UTILITY
# -------------------------------------------------------------
def get_cart_details(request):
    """
    Extracts session cart data and computes subtotal, discounts, and item info.
    Cart format in session:
    {
       "cake_id_str": {"quantity": 1, "weight": "1 kg", "custom_msg": ""}
    }
    Supports legacy format {"cake_id_str": quantity_int} for backward compatibility.
    """
    cart = request.session.get("cart", {})
    items = []
    subtotal = Decimal("0.00")
    total_count = 0

    cake_ids = [int(k) for k in cart.keys() if str(k).isdigit()]
    cakes_dict = {cake.id: cake for cake in Cake.objects.filter(id__in=cake_ids)}

    for key, val in cart.items():
        if not str(key).isdigit():
            continue
        cake_id = int(key)
        cake = cakes_dict.get(cake_id)
        if not cake or not cake.available:
            continue

        if isinstance(val, dict):
            qty = int(val.get("quantity", 1))
            weight = val.get("weight", "1 kg")
            custom_msg = val.get("custom_msg", "")
        else:
            qty = int(val)
            weight = "1 kg"
            custom_msg = ""

        if qty <= 0:
            continue

        # Weight multiplier: 0.5 kg = 0.6x, 1 kg = 1.0x, 1.5 kg = 1.5x, 2 kg = 1.9x
        multiplier = Decimal("1.0")
        if "0.5" in weight:
            multiplier = Decimal("0.6")
        elif "1.5" in weight:
            multiplier = Decimal("1.5")
        elif "2" in weight:
            multiplier = Decimal("1.9")

        unit_price = (cake.price * multiplier).quantize(Decimal("1.00"))
        item_total = unit_price * qty

        items.append({
            "cake": cake,
            "quantity": qty,
            "weight": weight,
            "custom_msg": custom_msg,
            "unit_price": unit_price,
            "subtotal": item_total,
        })
        subtotal += item_total
        total_count += qty

    coupon = request.session.get("coupon", {})
    discount = Decimal("0.00")
    if coupon and subtotal > Decimal("0.00"):
        percent = coupon.get("percent", 0)
        discount = (subtotal * Decimal(percent) / Decimal(100)).quantize(Decimal("1.00"))

    # Free delivery on orders over ₹700, otherwise ₹50
    delivery_fee = Decimal("0.00") if (subtotal >= Decimal("700.00") or subtotal == Decimal("0.00")) else Decimal("50.00")
    final_total = max(Decimal("0.00"), subtotal - discount + delivery_fee)

    progress_percent = min(100, int((subtotal / Decimal("700.00")) * 100)) if subtotal > Decimal("0.00") else 0
    is_free_delivery = subtotal >= Decimal("700.00")

    return {
        "items": items,
        "subtotal": subtotal,
        "discount": discount,
        "delivery_fee": delivery_fee,
        "total": final_total,
        "count": total_count,
        "coupon": coupon,
        "free_delivery_threshold": Decimal("700.00"),
        "amount_needed_for_free_delivery": max(Decimal("0.00"), Decimal("700.00") - subtotal),
        "delivery_progress_percent": progress_percent,
        "is_free_delivery": is_free_delivery,
    }


# -------------------------------------------------------------
# PUBLIC STOREFRONT VIEWS
# -------------------------------------------------------------
def home(request):
    """Artisanal storefront landing page with hero, featured cakes, categories, & testimonials."""
    cart_info = get_cart_details(request)
    featured_cakes = Cake.objects.filter(available=True)[:8]
    bestsellers = Cake.objects.filter(available=True)[:6]

    categories = [
        {"name": "Chocolate", "label": "Chocolate Obsession", "icon": "🍫", "badge": "Rich & Decadent"},
        {"name": "Cheesecake", "label": "Artisan Cheesecakes", "icon": "🍰", "badge": "Velvety Smooth"},
        {"name": "Fruit", "label": "Fresh Fruit & Berries", "icon": "🍓", "badge": "Farm Fresh"},
        {"name": "Exotic", "label": "Exotic & Signature", "icon": "✨", "badge": "Chef Specials"},
        {"name": "Eggless", "label": "100% Eggless Specials", "icon": "🌱", "badge": "Pure Veg"},
        {"name": "Pastry", "label": "Artisan Pastries", "icon": "🥐", "badge": "Flaky & Fresh"},
    ]

    return render(
        request,
        "shop/home.html",
        {
            "featured_cakes": featured_cakes,
            "bestsellers": bestsellers,
            "categories": categories,
            "cart_count": cart_info["count"],
            "cart_total": cart_info["total"],
        },
    )


def cakes(request):
    """Full gourmet cakes catalog with category tabs, search, dietary filter, and sorting."""
    cart_info = get_cart_details(request)
    all_cakes = Cake.objects.all()

    # Category filter
    category = request.GET.get("category", "").strip()
    if category and category != "All":
        all_cakes = all_cakes.filter(category=category)

    # Search filter
    search_query = request.GET.get("q", "").strip()
    if search_query:
        all_cakes = all_cakes.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Eggless filter
    eggless_only = request.GET.get("eggless") == "1"
    if eggless_only:
        all_cakes = all_cakes.filter(is_eggless=True)

    # Sorting
    sort_by = request.GET.get("sort", "featured")
    if sort_by == "price_low":
        all_cakes = all_cakes.order_by("price")
    elif sort_by == "price_high":
        all_cakes = all_cakes.order_by("-price")
    elif sort_by == "rating":
        all_cakes = all_cakes.order_by("-rating")
    else:
        all_cakes = all_cakes.order_by("-available", "-id")

    return render(
        request,
        "shop/cakes.html",
        {
            "cakes": all_cakes,
            "current_category": category or "All",
            "search_query": search_query,
            "eggless_only": eggless_only,
            "sort_by": sort_by,
            "cart_count": cart_info["count"],
        },
    )


def cake_detail(request, cake_id):
    """Cake detail view with weight selection, ingredients, reviews, and add to cart."""
    cake = get_object_or_404(Cake, id=cake_id)
    cart_info = get_cart_details(request)
    related_cakes = Cake.objects.filter(category=cake.category).exclude(id=cake.id)[:4]

    weight_list = [w.strip() for w in cake.weight_options.split(",") if w.strip()]

    return render(
        request,
        "shop/cake_detail.html",
        {
            "cake": cake,
            "related_cakes": related_cakes,
            "weight_list": weight_list,
            "cart_count": cart_info["count"],
        },
    )
def about(request):
    """Editorial storytelling page on bakery craftsmanship, ingredients, and heritage."""
    cart_info = get_cart_details(request)
    return render(request, "shop/about.html", {"cart_count": cart_info["count"]})


def contact(request):
    """Artisanal bakery flagship studio details, tasting hours, and inquiry form."""
    cart_info = get_cart_details(request)
    if request.method == "POST":
        messages.success(request, "💌 Thank you for contacting Sweet Slice! We look forward to sweetening your celebration.")
        return redirect("contact")
    return render(request, "shop/contact.html", {"cart_count": cart_info["count"]})


@csrf_exempt
def add_to_cart(request, cake_id):
    """Add cake to cart with selected weight, message, and quantity."""
    cake = get_object_or_404(Cake, id=cake_id, available=True)

    # Customer must be logged in to purchase / add to cart
    if not request.user.is_authenticated:
        redirect_target = request.POST.get("next") or reverse("cake_detail", kwargs={"cake_id": cake_id})
        login_url = f"{reverse('login')}?next={redirect_target}"

        if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1":
            return JsonResponse({
                "success": False,
                "require_login": True,
                "redirect_url": login_url,
                "message": "Please sign in to order this cake!",
            })

        messages.info(request, "✨ Please sign in or create an account to start adding cakes to your bag and order.")
        return redirect(login_url)

    cart = request.session.get("cart", {})
    key = str(cake.id)

    qty_to_add = int(request.POST.get("quantity", 1))
    weight = request.POST.get("weight", "1 kg")
    custom_msg = request.POST.get("custom_msg", "").strip()

    if key in cart and isinstance(cart[key], dict):
        cart[key]["quantity"] = cart[key].get("quantity", 0) + qty_to_add
        if weight:
            cart[key]["weight"] = weight
        if custom_msg:
            cart[key]["custom_msg"] = custom_msg
    else:
        cart[key] = {
            "quantity": qty_to_add,
            "weight": weight,
            "custom_msg": custom_msg,
        }

    request.session["cart"] = cart
    request.session.modified = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1":
        cart_info = get_cart_details(request)
        return JsonResponse({
            "success": True,
            "message": f"Added {cake.name} to cart!",
            "cart_count": cart_info["count"],
            "cart_total": float(cart_info["total"]),
        })

    messages.success(request, f"✨ Added '{cake.name}' to your cart!")
    return redirect(request.POST.get("next") or "cakes")


@csrf_exempt
def update_cart_quantity(request, cake_id):
    """Increment or decrement quantity directly in cart."""
    cart = request.session.get("cart", {})
    key = str(cake_id)
    action = request.POST.get("action", "inc")

    if key in cart:
        if isinstance(cart[key], dict):
            current_qty = cart[key].get("quantity", 1)
            if action == "inc":
                cart[key]["quantity"] = current_qty + 1
            elif action == "dec":
                if current_qty > 1:
                    cart[key]["quantity"] = current_qty - 1
                else:
                    del cart[key]
        else:
            current_qty = int(cart[key])
            if action == "inc":
                cart[key] = current_qty + 1
            elif action == "dec":
                if current_qty > 1:
                    cart[key] = current_qty - 1
                else:
                    del cart[key]

        request.session["cart"] = cart
        request.session.modified = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1":
        cart_info = get_cart_details(request)
        return JsonResponse({
            "success": True,
            "cart_count": cart_info["count"],
            "cart_total": float(cart_info["total"]),
            "subtotal": float(cart_info["subtotal"]),
            "discount": float(cart_info["discount"]),
            "delivery_fee": float(cart_info["delivery_fee"]),
        })

    return redirect("cart")


def remove_from_cart(request, cake_id):
    """Remove a cake completely from the cart."""
    cart = request.session.get("cart", {})
    key = str(cake_id)
    if key in cart:
        del cart[key]
        request.session["cart"] = cart
        request.session.modified = True
        messages.info(request, "Item removed from cart.")

    return redirect("cart")


def clear_cart(request):
    """Clear entire session cart."""
    request.session["cart"] = {}
    request.session["coupon"] = {}
    request.session.modified = True
    messages.info(request, "Your cart has been cleared.")
    return redirect("cakes")


def apply_coupon(request):
    """Apply discount code (e.g. SWEET20, FIRSTCAKE)."""
    code = request.POST.get("code", "").strip().upper()
    valid_coupons = {
        "SWEET20": {"percent": 20, "desc": "20% Special Bakery Discount"},
        "FIRSTCAKE": {"percent": 15, "desc": "15% First Order Welcome Discount"},
        "SWEET50": {"percent": 10, "desc": "10% Celebration Bonanza"},
    }

    if code in valid_coupons:
        request.session["coupon"] = {
            "code": code,
            "percent": valid_coupons[code]["percent"],
            "desc": valid_coupons[code]["desc"],
        }
        request.session.modified = True
        messages.success(request, f"🎉 Coupon '{code}' applied! You get {valid_coupons[code]['percent']}% off!")
    else:
        messages.error(request, "Invalid coupon code. Try SWEET20 or FIRSTCAKE.")

    return redirect("cart")


def remove_coupon(request):
    """Remove applied coupon."""
    if "coupon" in request.session:
        del request.session["coupon"]
        request.session.modified = True
        messages.info(request, "Coupon removed.")
    return redirect("cart")


def cart(request):
    """Interactive cart page with quantity adjustment, coupons, and delivery calculation."""
    if not request.user.is_authenticated:
        messages.info(request, "✨ Please sign in to view your bag and complete your order.")
        return redirect(f"{reverse('login')}?next={reverse('cart')}")

    cart_info = get_cart_details(request)
    return render(
        request,
        "shop/cart.html",
        {
            "cart_info": cart_info,
            "cart_count": cart_info["count"],
        },
    )


# -------------------------------------------------------------
# CHECKOUT & RAZORPAY INTEGRATION
# -------------------------------------------------------------
def checkout(request):
    """
    Checkout page: Collects customer contact, delivery destination, and chosen payment method.
    If Razorpay is selected, saves delivery details to session and redirects to dedicated payment gateway page.
    If Cash on Delivery is selected, creates pending order immediately.
    """
    if not request.user.is_authenticated:
        messages.info(request, "✨ Please sign in to proceed to checkout and place your order.")
        return redirect(f"{reverse('login')}?next={reverse('checkout')}")

    cart_info = get_cart_details(request)

    if not cart_info["items"]:
        messages.warning(request, "Your cart is empty. Please select some delicious cakes first!")
        return redirect("cakes")

    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "Razorpay (Online)").strip()
        checkout_data = {
            "name": request.POST.get("name", "").strip() or request.user.get_full_name() or request.user.username,
            "phone": request.POST.get("phone", "").strip() or "+91 98201 12345",
            "email": request.POST.get("email", "").strip() or request.user.email or "patron@sweetslice.com",
            "address": request.POST.get("address", "").strip() or "Boutique Storefront Pickup",
            "delivery_date": request.POST.get("delivery_date", "").strip() or "Today (Express)",
            "delivery_slot": request.POST.get("delivery_slot", "").strip() or "Afternoon Slot",
            "cake_message": request.POST.get("cake_message", "").strip(),
            "payment_method": payment_method,
        }
        request.session["checkout_data"] = checkout_data
        request.session.modified = True

        if payment_method in ["Cash on Delivery", "COD"]:
            return process_razorpay_payment(request)
        else:
            return redirect("payment_gateway")

    # Pre-fill customer details from session or logged in user
    checkout_data = request.session.get("checkout_data", {})
    default_name = checkout_data.get("name") or request.user.get_full_name() or request.user.username
    default_email = checkout_data.get("email") or request.user.email or ""
    default_phone = checkout_data.get("phone") or ""
    default_address = checkout_data.get("address") or ""

    return render(
        request,
        "shop/checkout.html",
        {
            "cart_info": cart_info,
            "cart_count": cart_info["count"],
            "default_name": default_name,
            "default_email": default_email,
            "default_phone": default_phone,
            "default_address": default_address,
            "checkout_data": checkout_data,
        },
    )


def payment_gateway(request):
    """
    Dedicated, authentic Razorpay Secure Payment Gateway page.
    Renders high-fidelity checkout with UPI (QR + Apps), Cards, Netbanking, and Wallets.
    """
    if not request.user.is_authenticated:
        return redirect("login")

    cart_info = get_cart_details(request)
    if not cart_info["items"]:
        messages.warning(request, "Your cart is empty. Please select some delicious cakes first!")
        return redirect("cakes")

    checkout_data = request.session.get("checkout_data", {})
    if not checkout_data:
        checkout_data = {
            "name": request.user.get_full_name() or request.user.username,
            "phone": "+91 98201 12345",
            "email": request.user.email or "patron@sweetslice.com",
            "address": "Atelier Priority Delivery, NH12, Krishnanagar",
            "delivery_date": "Today (Express)",
            "delivery_slot": "2:00 PM - 6:00 PM",
            "cake_message": "",
            "payment_method": "Razorpay (Online)",
        }
        request.session["checkout_data"] = checkout_data
        request.session.modified = True

    razorpay_key_id = getattr(settings, "RAZORPAY_KEY_ID", "rzp_test_SweetSliceBakeryDemo")

    return render(
        request,
        "shop/payment_gateway.html",
        {
            "cart_info": cart_info,
            "cart_count": cart_info["count"],
            "checkout_data": checkout_data,
            "razorpay_key_id": razorpay_key_id,
            "razorpay_amount": int(cart_info["total"] * 100),
        },
    )


@csrf_exempt
def process_razorpay_payment(request):
    """
    Processes Razorpay payment callback (both real or demo simulation) or Cash on Delivery.
    Creates Order record with payment details, clears cart, and redirects to order receipt.
    """
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method != "POST":
        return redirect("checkout")

    cart_info = get_cart_details(request)
    if not cart_info["items"]:
        return redirect("cakes")

    checkout_data = request.session.get("checkout_data", {})
    name = request.POST.get("name", "").strip() or checkout_data.get("name") or request.user.get_full_name() or request.user.username
    phone = request.POST.get("phone", "").strip() or checkout_data.get("phone") or "+91 98765 43210"
    email = request.POST.get("email", "").strip() or checkout_data.get("email") or request.user.email or "guest@sweetslice.com"
    address = request.POST.get("address", "").strip() or checkout_data.get("address") or "Local Delivery Address"
    delivery_date = request.POST.get("delivery_date", "").strip() or checkout_data.get("delivery_date") or "Today (Express)"
    delivery_slot = request.POST.get("delivery_slot", "").strip() or checkout_data.get("delivery_slot") or "Afternoon Slot"
    cake_message = request.POST.get("cake_message", "").strip() or checkout_data.get("cake_message", "")
    payment_method = request.POST.get("payment_method", "").strip() or checkout_data.get("payment_method", "Razorpay (Online)")

    razorpay_payment_id = request.POST.get("razorpay_payment_id", "").strip()
    razorpay_order_id = request.POST.get("razorpay_order_id", "").strip()

    is_cod = "Cash on Delivery" in payment_method or payment_method in ["COD", "Cash On Delivery"]

    if not razorpay_payment_id:
        import uuid
        if is_cod:
            razorpay_payment_id = f"cod_{uuid.uuid4().hex[:8].upper()}"
        else:
            razorpay_payment_id = f"pay_rzp_{uuid.uuid4().hex[:10]}"

    payment_status = "Pending" if is_cod else "Paid"

    # Serialize items
    items_summary_list = []
    items_json_list = []
    for item in cart_info["items"]:
        summary_str = f"{item['cake'].name} ({item['weight']}) x {item['quantity']}"
        items_summary_list.append(summary_str)
        items_json_list.append({
            "cake_id": item["cake"].id,
            "name": item["cake"].name,
            "weight": item["weight"],
            "quantity": item["quantity"],
            "price": float(item["unit_price"]),
            "subtotal": float(item["subtotal"]),
            "image_url": item["cake"].image_url,
            "custom_msg": item["custom_msg"],
        })

    order = Order.objects.create(
        customer_name=name,
        phone=phone,
        email=email,
        address=address,
        delivery_date=delivery_date,
        delivery_slot=delivery_slot,
        cake_message=cake_message,
        items=", ".join(items_summary_list),
        items_json=json.dumps(items_json_list),
        subtotal=cart_info["subtotal"],
        discount=cart_info["discount"],
        delivery_fee=cart_info["delivery_fee"],
        total=cart_info["total"],
        payment_method=payment_method,
        payment_status=payment_status,
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=razorpay_payment_id,
        order_status="Order Placed",
    )

    # Empty cart & clear checkout session
    request.session["cart"] = {}
    request.session["coupon"] = {}
    request.session["checkout_data"] = {}
    request.session.modified = True

    return redirect("order_success", order_number=order.order_number)


def order_success(request, order_number):
    """Displays celebratory order receipt with delivery tracking timeline."""
    order = get_object_or_404(Order, order_number=order_number)
    try:
        items_detail = json.loads(order.items_json)
    except Exception:
        items_detail = []

    return render(
        request,
        "shop/order_success.html",
        {
            "order": order,
            "items_detail": items_detail,
            "cart_count": 0,
        },
    )


def track_order(request):
    """Customer order tracking lookup by order number or phone."""
    query = request.GET.get("q", "").strip()
    order = None
    orders_found = []

    if query:
        orders_found = Order.objects.filter(
            Q(order_number__iexact=query) | Q(phone__icontains=query)
        ).order_by("-created_at")
        if orders_found.exists():
            order = orders_found.first()

    return render(
        request,
        "shop/track_order.html",
        {
            "query": query,
            "order": order,
            "orders_found": orders_found,
            "cart_count": get_cart_details(request)["count"],
        },
    )


# -------------------------------------------------------------
# USER AUTHENTICATION (CUSTOMER PORTAL)
# -------------------------------------------------------------
def user_login(request):
    """
    Luxury boutique customer login view.
    Supports login via username or email address, with automatic return-to-product redirection.
    """
    next_url = request.GET.get("next") or request.POST.get("next") or ""
    if next_url == "None" or not next_url:
        next_url = ""

    if request.user.is_authenticated:
        return redirect(next_url or "home")

    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not identifier or not password:
            messages.error(request, "Please enter both your username/email and password.")
            return render(request, "shop/login.html", {
                "next": next_url,
                "active_tab": "login",
                "identifier": identifier,
                "cart_count": get_cart_details(request)["count"],
            })

        username_to_auth = identifier
        # Allow email as identifier
        user_by_email = User.objects.filter(email__iexact=identifier).first()
        if user_by_email:
            username_to_auth = user_by_email.username

        user = authenticate(request, username=username_to_auth, password=password)
        if user is not None:
            login(request, user)
            display_name = user.first_name or user.username
            messages.success(request, f"✨ Welcome back, {display_name}! Ready for fresh patisserie.")
            if next_url:
                return redirect(next_url)
            return redirect("home")
        else:
            messages.error(request, "Incorrect username/email or password. Please verify and try again.")
            return render(request, "shop/login.html", {
                "next": next_url,
                "active_tab": "login",
                "identifier": identifier,
                "cart_count": get_cart_details(request)["count"],
            })

    return render(request, "shop/login.html", {
        "next": next_url,
        "active_tab": "login",
        "cart_count": get_cart_details(request)["count"],
    })


def user_register(request):
    """
    Customer account registration view.
    Creates account and automatically signs user in, seamlessly preserving shopping flow.
    """
    next_url = request.GET.get("next") or request.POST.get("next") or ""
    if next_url == "None" or not next_url:
        next_url = ""

    if request.user.is_authenticated:
        return redirect(next_url or "home")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        errors = []
        if not username or not email or not password:
            errors.append("Please fill in your name, username, email, and password.")
        elif len(password) < 4:
            errors.append("Password must be at least 4 characters long.")
        elif password != confirm_password:
            errors.append("Passwords do not match. Please re-enter carefully.")
        elif User.objects.filter(username__iexact=username).exists():
            errors.append(f"The username '{username}' is already taken. Please pick another.")
        elif User.objects.filter(email__iexact=email).exists():
            errors.append(f"An account with email '{email}' already exists. Please sign in.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, "shop/login.html", {
                "next": next_url,
                "active_tab": "register",
                "reg_full_name": full_name,
                "reg_username": username,
                "reg_email": email,
                "cart_count": get_cart_details(request)["count"],
            })

        first_name = full_name.split()[0] if full_name else username
        last_name = " ".join(full_name.split()[1:]) if " " in full_name else ""
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        login(request, user)
        messages.success(request, f"🎉 Welcome to Sweet Slice, {first_name}! Your account is ready.")
        if next_url:
            return redirect(next_url)
        return redirect("home")

    return render(request, "shop/login.html", {
        "next": next_url,
        "active_tab": "register",
        "cart_count": get_cart_details(request)["count"],
    })

def user_logout(request):
    """Sign user out and redirect gracefully."""
    logout(request)
    messages.info(request, "You have been safely signed out. We hope to sweeten your celebrations soon! 🍰")
    return redirect("home")


# -------------------------------------------------------------
# ADMIN DASHBOARD VIEWS
# -------------------------------------------------------------

def _is_admin(request):
    """Returns True if the current session has admin access enabled."""
    return request.session.get("is_admin", False)


def admin_quick_auth(request):
    """Toggle admin mode on/off via a simple session flag (no login required for demo)."""
    if _is_admin(request):
        request.session["is_admin"] = False
        messages.info(request, "Admin mode disabled.")
    else:
        request.session["is_admin"] = True
        messages.success(request, "Admin mode enabled. Welcome back, Executive! 👑")
    return redirect("admin_dashboard")


def admin_dashboard(request):
    """Executive bakery dashboard: KPIs, cake catalog management, live order pipeline."""
    cakes = Cake.objects.all().order_by("-id")
    orders = Order.objects.all().order_by("-created_at")

    # Status filter
    status_filter = request.GET.get("order_status", "")
    if status_filter:
        orders = orders.filter(order_status=status_filter)

    # KPIs
    from django.db.models import Sum
    total_sales = Order.objects.filter(payment_status="Paid").aggregate(t=Sum("total"))["t"] or 0
    total_orders = Order.objects.count()
    active_statuses = ["Order Placed", "Baking in Oven", "Decorating & Packing", "Out for Delivery"]
    active_orders_count = Order.objects.filter(order_status__in=active_statuses).count()
    available_cakes_count = Cake.objects.filter(available=True).count()
    total_cakes_count = Cake.objects.count()

    status_choices = [sc[0] for sc in Order.STATUS_CHOICES]

    return render(request, "shop/admin_dashboard.html", {
        "cakes": cakes,
        "orders": orders,
        "status_filter": status_filter,
        "status_choices": status_choices,
        "total_sales": total_sales,
        "total_orders": total_orders,
        "active_orders_count": active_orders_count,
        "available_cakes_count": available_cakes_count,
        "total_cakes_count": total_cakes_count,
        "is_admin": _is_admin(request),
        "cart_count": get_cart_details(request)["count"],
    })


def admin_add_cake(request):
    """Add a new cake to the catalog from the admin dashboard modal form."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category = request.POST.get("category", "Chocolate")
        price = request.POST.get("price", "0")
        original_price = request.POST.get("original_price", "") or None
        image_url = request.POST.get("image_url", "").strip()
        badge = request.POST.get("badge", "").strip()
        weight_options = request.POST.get("weight_options", "0.5 kg, 1 kg, 1.5 kg, 2 kg").strip()
        description = request.POST.get("description", "").strip()
        is_eggless = bool(request.POST.get("is_eggless"))
        available = bool(request.POST.get("available"))

        if name and price:
            Cake.objects.create(
                name=name,
                category=category,
                price=Decimal(price),
                original_price=Decimal(original_price) if original_price else None,
                image_url=image_url,
                badge=badge,
                weight_options=weight_options,
                description=description,
                is_eggless=is_eggless,
                available=available,
            )
            messages.success(request, f"🎂 '{name}' has been added to the menu successfully!")
        else:
            messages.error(request, "Cake name and price are required.")

    return redirect("admin_dashboard")


def admin_edit_cake(request, cake_id):
    """GET: return cake data as JSON for modal population. POST: save edits."""
    cake = get_object_or_404(Cake, id=cake_id)

    if request.method == "GET":
        return JsonResponse({
            "id": cake.id,
            "name": cake.name,
            "category": cake.category,
            "price": str(cake.price),
            "original_price": str(cake.original_price) if cake.original_price else "",
            "image_url": cake.image_url,
            "badge": cake.badge,
            "weight_options": cake.weight_options,
            "description": cake.description,
            "is_eggless": cake.is_eggless,
            "available": cake.available,
        })

    if request.method == "POST":
        cake.name = request.POST.get("name", cake.name).strip()
        cake.category = request.POST.get("category", cake.category)
        price = request.POST.get("price", "")
        if price:
            cake.price = Decimal(price)
        original_price = request.POST.get("original_price", "")
        cake.original_price = Decimal(original_price) if original_price else None
        cake.image_url = request.POST.get("image_url", cake.image_url).strip()
        cake.badge = request.POST.get("badge", "").strip()
        cake.weight_options = request.POST.get("weight_options", cake.weight_options).strip()
        cake.description = request.POST.get("description", "").strip()
        cake.is_eggless = bool(request.POST.get("is_eggless"))
        cake.available = bool(request.POST.get("available"))
        cake.save()
        messages.success(request, f"✏️ '{cake.name}' updated successfully!")
        return redirect("admin_dashboard")

    return redirect("admin_dashboard")


def admin_delete_cake(request, cake_id):
    """Permanently delete a cake from the catalog."""
    cake = get_object_or_404(Cake, id=cake_id)
    name = cake.name
    cake.delete()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True, "cake_id": cake_id, "message": f"'{name}' deleted successfully."})
    messages.success(request, f"🗑️ '{name}' removed from the menu.")
    return redirect("admin_dashboard")


def admin_toggle_cake_availability(request, cake_id):
    """Toggle a cake between In Stock and Out of Stock."""
    cake = get_object_or_404(Cake, id=cake_id)
    cake.available = not cake.available
    cake.save()
    status = "In Stock" if cake.available else "Out of Stock"
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True, "cake_id": cake.id, "available": cake.available, "status": status})
    messages.info(request, f"'{cake.name}' is now marked as {status}.")
    return redirect("admin_dashboard")


def admin_update_order_status(request, order_id):
    """Update order pipeline status from the admin dashboard."""
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get("order_status", "")
        valid_statuses = [sc[0] for sc in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            order.order_status = new_status
            order.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "order_id": order.id, "new_status": new_status, "order_number": order.order_number})
            messages.success(request, f"Order #{order.order_number} → {new_status}")
    return redirect("admin_dashboard")
