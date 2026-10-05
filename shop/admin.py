from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Cake, Order


# ──────────────────────────────────────────────
# Custom Admin Site Header / Branding
# ──────────────────────────────────────────────
admin.site.site_header  = "🍰 Sweet Slice Patisserie"
admin.site.site_title   = "Sweet Slice Admin"
admin.site.index_title  = "Bakery Management Panel"


# ──────────────────────────────────────────────
# CAKE ADMIN
# ──────────────────────────────────────────────
@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    # Columns shown in the list view
    list_display = (
        "cake_thumbnail",
        "name",
        "category",
        "price",
        "original_price",
        "badge_display",
        "rating",
        "reviews_count",
        "is_eggless",
        "available",
        "created_at",
    )

    # Sidebar filters
    list_filter = ("category", "available", "is_eggless", "badge")

    # Search bar
    search_fields = ("name", "description", "badge")

    # Inline-edit from the list page
    list_editable = ("price", "available")

    # Pre-filled slug / ordering
    ordering = ("-id",)

    # Date drill-down sidebar
    date_hierarchy = "created_at"

    # How many rows per page
    list_per_page = 20

    # Read-only audit fields
    readonly_fields = ("created_at", "cake_preview")

    # Organised edit form with sections
    fieldsets = (
        ("📝 Basic Information", {
            "fields": ("name", "category", "description"),
        }),
        ("💰 Pricing", {
            "fields": ("price", "original_price"),
            "description": "Set 'Original Price' to show a strikethrough discount.",
        }),
        ("🖼️ Image", {
            "fields": ("image_url", "cake_preview"),
            "description": "Paste any public image URL (Unsplash, CDN, etc.)",
        }),
        ("⚙️ Details & Options", {
            "fields": ("badge", "rating", "reviews_count", "is_eggless", "weight_options", "available"),
        }),
        ("🕒 Audit", {
            "fields": ("created_at",),
            "classes": ("collapse",),
        }),
    )

    # ── Custom column: tiny thumbnail in list view ──
    @admin.display(description="Photo")
    def cake_thumbnail(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width:52px;height:52px;object-fit:cover;'
                'border-radius:8px;border:1px solid #ddd;" />',
                obj.image_url,
            )
        return "—"

    # ── Custom column: styled badge chip ──
    @admin.display(description="Badge")
    def badge_display(self, obj):
        if not obj.badge:
            return "—"
        colours = {
            "Bestseller":     "#96354B",
            "Chef's Special": "#B88246",
            "Trending":       "#1E824C",
            "New":            "#2563EB",
            "Eggless":        "#7C3AED",
        }
        colour = colours.get(obj.badge, "#555")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 9px;'
            'border-radius:99px;font-size:11px;font-weight:600;">{}</span>',
            colour, obj.badge,
        )

    # ── Detail view: large preview image ──
    @admin.display(description="Preview")
    def cake_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-width:340px;border-radius:14px;'
                'border:1px solid #e0d9d0;" />',
                obj.image_url,
            )
        return "No image URL set."


# ──────────────────────────────────────────────
# ORDER ADMIN
# ──────────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "phone",
        "items_short",
        "total_display",
        "payment_status",
        "order_status",
        "delivery_date",
        "created_at",
    )

    list_filter = ("order_status", "payment_status", "delivery_date", "created_at")

    search_fields = (
        "order_number",
        "customer_name",
        "phone",
        "email",
        "razorpay_payment_id",
    )

    # Inline-edit key fields directly from the list
    list_editable = ("order_status", "payment_status")


    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    list_per_page = 25

    # These fields must never be overwritten
    readonly_fields = (
        "order_number",
        "created_at",
        "items_detail_display",
        "razorpay_payment_id",
        "razorpay_order_id",
    )

    fieldsets = (
        ("📦 Order Info", {
            "fields": ("order_number", "order_status", "created_at"),
        }),
        ("👤 Customer", {
            "fields": ("customer_name", "phone", "email", "address"),
        }),
        ("🚚 Delivery", {
            "fields": ("delivery_date", "delivery_slot"),
        }),
        ("🎂 Items", {
            "fields": ("items", "items_detail_display", "cake_message"),
        }),
        ("💳 Payment", {
            "fields": (
                "payment_method",
                "payment_status",
                "subtotal",
                "discount",
                "delivery_fee",
                "total",
                "razorpay_order_id",
                "razorpay_payment_id",
            ),
        }),
    )

    # ── Truncated items summary ──
    @admin.display(description="Items")
    def items_short(self, obj):
        txt = obj.items or "—"
        return txt[:55] + "…" if len(txt) > 55 else txt

    # ── Styled total amount ──
    @admin.display(description="Total")
    def total_display(self, obj):
        return format_html('<strong style="color:#221614;">₹{}</strong>', obj.total)

    # ── Coloured payment status badge ──
    @admin.display(description="Payment")
    def payment_status_badge(self, obj):
        colour_map = {"Paid": "#1E824C", "Pending": "#B88246", "Failed": "#DC2626"}
        colour = colour_map.get(obj.payment_status, "#555")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 9px;'
            'border-radius:99px;font-size:11px;font-weight:600;">{}</span>',
            colour, obj.payment_status,
        )

    # ── Coloured order status badge ──
    @admin.display(description="Status")
    def order_status_badge(self, obj):
        colour_map = {
            "Order Placed":         "#2563EB",
            "Baking in Oven":       "#D97706",
            "Decorating & Packing": "#7C3AED",
            "Out for Delivery":     "#0891B2",
            "Delivered":            "#1E824C",
            "Cancelled":            "#DC2626",
        }
        colour = colour_map.get(obj.order_status, "#555")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 9px;'
            'border-radius:99px;font-size:11px;font-weight:600;">{}</span>',
            colour, obj.order_status,
        )

    # ── Rich items breakdown in detail view ──
    @admin.display(description="Items Breakdown")
    def items_detail_display(self, obj):
        import json
        try:
            items = json.loads(obj.items_json)
        except Exception:
            return obj.items or "—"
        if not items:
            return obj.items or "—"
        rows = "".join(
            f"<tr>"
            f"<td style='padding:6px 10px;border-bottom:1px solid #eee;'>{i.get('name','')}</td>"
            f"<td style='padding:6px 10px;border-bottom:1px solid #eee;'>{i.get('weight','')}</td>"
            f"<td style='padding:6px 10px;border-bottom:1px solid #eee;'>× {i.get('quantity','')}</td>"
            f"<td style='padding:6px 10px;border-bottom:1px solid #eee;font-weight:600;'>₹{i.get('subtotal','')}</td>"
            f"</tr>"
            for i in items
        )
        return mark_safe(
            f"<table style='border-collapse:collapse;font-size:13px;width:100%;'>"
            f"<thead><tr style='background:#f5f0ea;'>"
            f"<th style='padding:6px 10px;text-align:left;'>Cake</th>"
            f"<th style='padding:6px 10px;text-align:left;'>Size</th>"
            f"<th style='padding:6px 10px;text-align:left;'>Qty</th>"
            f"<th style='padding:6px 10px;text-align:left;'>Amount</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>"
        )
