from django.urls import path
from . import views

urlpatterns = [
    # Storefront pages
    path("", views.home, name="home"),
    path("cakes/", views.cakes, name="cakes"),
    path("collections/", views.cakes, name="collections"),
    path("cake/<int:cake_id>/", views.cake_detail, name="cake_detail"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    # Cart operations
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:cake_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:cake_id>/", views.update_cart_quantity, name="update_cart_quantity"),
    path("cart/remove/<int:cake_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("cart/coupon/apply/", views.apply_coupon, name="apply_coupon"),
    path("cart/coupon/remove/", views.remove_coupon, name="remove_coupon"),

    # Checkout & Razorpay
    path("checkout/", views.checkout, name="checkout"),
    path("payment/", views.payment_gateway, name="payment_gateway"),
    path("payment/process/", views.process_razorpay_payment, name="process_razorpay_payment"),
    path("order/success/<str:order_number>/", views.order_success, name="order_success"),
    path("track-order/", views.track_order, name="track_order"),

    # Customer Authentication
    path("login/", views.user_login, name="login"),
    path("register/", views.user_register, name="register"),
    path("logout/", views.user_logout, name="logout"),

    # Admin Dashboard
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/auth/", views.admin_quick_auth, name="admin_quick_auth"),
    path("dashboard/cake/add/", views.admin_add_cake, name="admin_add_cake"),
    path("dashboard/cake/edit/<int:cake_id>/", views.admin_edit_cake, name="admin_edit_cake"),
    path("dashboard/cake/delete/<int:cake_id>/", views.admin_delete_cake, name="admin_delete_cake"),
    path("dashboard/cake/toggle/<int:cake_id>/", views.admin_toggle_cake_availability, name="admin_toggle_cake_availability"),
    path("dashboard/order/status/<int:order_id>/", views.admin_update_order_status, name="admin_update_order_status"),
]
