import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from shop.models import Cake, Order


class Command(BaseCommand):
    help = "Seed database with artisanal cakes, categories, and sample orders."

    def handle(self, *args, **options):
        # 1. Ensure superuser exists for testing
        admin_user, created = User.objects.get_or_create(username="admin")
        if created or not admin_user.has_usable_password():
            admin_user.set_password("admin123")
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.email = "admin@sweetslice.com"
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Superuser created: admin / admin123"))

        # 2. Gourmet Cakes Data
        cakes_data = [
            {
                "name": "Belgian Dark Chocolate Truffle",
                "category": "Chocolate",
                "description": "Intense 70% Belgian chocolate ganache layered with moist cocoa sponge, dusted with French cocoa powder.",
                "price": Decimal("799.00"),
                "original_price": Decimal("999.00"),
                "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=700&auto=format&fit=crop&q=80",
                "badge": "Bestseller",
                "rating": Decimal("4.9"),
                "reviews_count": 142,
                "is_eggless": False,
                "weight_options": "0.5 kg, 1 kg, 1.5 kg, 2 kg",
            },
            {
                "name": "Classic Red Velvet Royale",
                "category": "Exotic",
                "description": "Velvety crimson sponge layered with our signature Madagascar vanilla cream cheese frosting and ruby crumble.",
                "price": Decimal("749.00"),
                "original_price": Decimal("899.00"),
                "image_url": "https://images.unsplash.com/photo-1616541823729-00fe0aacd32c?w=700&auto=format&fit=crop&q=80",
                "badge": "Chef's Special",
                "rating": Decimal("4.8"),
                "reviews_count": 98,
                "is_eggless": True,
                "weight_options": "0.5 kg, 1 kg, 2 kg",
            },
            {
                "name": "Lotus Biscoff Caramel Cheesecake",
                "category": "Cheesecake",
                "description": "Velvety baked Philadelphia cream cheese on a crunchy Biscoff speculoos crust, smothered in warm molten Biscoff spread.",
                "price": Decimal("899.00"),
                "original_price": Decimal("1099.00"),
                "image_url": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=700&auto=format&fit=crop&q=80",
                "badge": "Trending",
                "rating": Decimal("5.0"),
                "reviews_count": 215,
                "is_eggless": True,
                "weight_options": "0.5 kg, 1 kg",
            },
            {
                "name": "Wild Blueberry Glaze Cheesecake",
                "category": "Cheesecake",
                "description": "Rich artisanal baked cheesecake topped with a compote of freshly simmered Canadian blueberries.",
                "price": Decimal("849.00"),
                "original_price": Decimal("999.00"),
                "image_url": "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=700&auto=format&fit=crop&q=80",
                "badge": "Top Rated",
                "rating": Decimal("4.9"),
                "reviews_count": 86,
                "is_eggless": False,
                "weight_options": "0.5 kg, 1 kg, 1.5 kg",
            },
            {
                "name": "Royal Black Forest Gateau",
                "category": "Chocolate",
                "description": "Layers of Dutch chocolate sponge, kirsch-infused whipped dairy cream, dark chocolate curls, and maraschino cherries.",
                "price": Decimal("649.00"),
                "original_price": Decimal("799.00"),
                "image_url": "https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?w=700&auto=format&fit=crop&q=80",
                "badge": "Classic",
                "rating": Decimal("4.7"),
                "reviews_count": 164,
                "is_eggless": True,
                "weight_options": "0.5 kg, 1 kg, 2 kg",
            },
            {
                "name": "Golden Butterscotch Praline",
                "category": "Exotic",
                "description": "Golden caramelized butterscotch crunch infused with silky smooth vanilla whip and butter-caramel drizzle.",
                "price": Decimal("599.00"),
                "original_price": Decimal("699.00"),
                "image_url": "https://images.unsplash.com/photo-1542826438-bd32f43d626f?w=700&auto=format&fit=crop&q=80",
                "badge": "Popular",
                "rating": Decimal("4.8"),
                "reviews_count": 73,
                "is_eggless": True,
                "weight_options": "0.5 kg, 1 kg, 1.5 kg",
            },
            {
                "name": "Alphonso Mango Sunshine Gateau",
                "category": "Fruit",
                "description": "Fresh seasonal Ratnagiri Alphonso mango pulp blended with light chiffon sponge and white chocolate flakes.",
                "price": Decimal("749.00"),
                "original_price": Decimal("899.00"),
                "image_url": "https://images.unsplash.com/photo-1519869325930-281384150729?w=800&auto=format&fit=crop&q=80",
                "badge": "Seasonal Star",
                "rating": Decimal("4.9"),
                "reviews_count": 119,
                "is_eggless": True,
                "weight_options": "0.5 kg, 1 kg",
            },
            {
                "name": "Persian Pistachio & Rose Petal",
                "category": "Eggless",
                "description": "Fragrant cardamom-infused pistachio sponge decorated with organic edible dried rose petals and crushed Iranian pistachios.",
                "price": Decimal("899.00"),
                "original_price": Decimal("1049.00"),
                "image_url": "https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?w=700&auto=format&fit=crop&q=80",
                "badge": "Artisanal",
                "rating": Decimal("4.9"),
                "reviews_count": 67,
                "is_eggless": True,
                "weight_options": "0.5 kg, 1 kg, 2 kg",
            },
            {
                "name": "Italian Tiramisu Espresso Cloud",
                "category": "Exotic",
                "description": "Savoiardi sponge soaked in freshly brewed Italian espresso, folded with mascarpone cream and cocoa dust.",
                "price": Decimal("849.00"),
                "original_price": Decimal("999.00"),
                "image_url": "https://images.unsplash.com/photo-1571115177098-24ec42ed204d?w=700&auto=format&fit=crop&q=80",
                "badge": "Coffee Lover",
                "rating": Decimal("4.8"),
                "reviews_count": 89,
                "is_eggless": False,
                "weight_options": "0.5 kg, 1 kg",
            },
            {
                "name": "Ferrero Rocher Hazelnut Crunch",
                "category": "Chocolate",
                "description": "Crunchy toasted hazelnuts, molten Nutella frosting, wafer crumb base, and whole Ferrero Rocher truffles on top.",
                "price": Decimal("949.00"),
                "original_price": Decimal("1199.00"),
                "image_url": "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=700&auto=format&fit=crop&q=80",
                "badge": "Decadent",
                "rating": Decimal("5.0"),
                "reviews_count": 182,
                "is_eggless": False,
                "weight_options": "0.5 kg, 1 kg, 2 kg",
            },
            {
                "name": "Fresh Strawberry Shortcake Cloud",
                "category": "Fruit",
                "description": "Fluffy Japanese-style genoise sponge with slices of sweet strawberries and cloud-light chantilly cream.",
                "price": Decimal("699.00"),
                "original_price": Decimal("849.00"),
                "image_url": "https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=700&auto=format&fit=crop&q=80",
                "badge": "Summer Fresh",
                "rating": Decimal("4.7"),
                "reviews_count": 94,
                "is_eggless": True,
                "weight_options": "0.5 kg, 1 kg",
            },
            {
                "name": "New York Baked Cheesecake",
                "category": "Cheesecake",
                "description": "Authentic dense and creamy slow-baked New York cheesecake with a buttery graham cracker crust and lemon zest hint.",
                "price": Decimal("799.00"),
                "original_price": Decimal("949.00"),
                "image_url": "https://images.unsplash.com/photo-1524351199678-941a58a3df50?w=700&auto=format&fit=crop&q=80",
                "badge": "All-Time Fav",
                "rating": Decimal("4.9"),
                "reviews_count": 112,
                "is_eggless": False,
                "weight_options": "0.5 kg, 1 kg, 1.5 kg",
            },
        ]

        created_count = 0
        for data in cakes_data:
            cake, was_created = Cake.objects.update_or_create(
                name=data["name"],
                defaults=data,
            )
            if was_created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Artisanal cakes catalog updated ({len(cakes_data)} cakes ready)."))

        # 3. Sample Orders for Dashboard Analytics
        if Order.objects.count() == 0:
            sample_orders = [
                {
                    "customer_name": "Aanya Sharma",
                    "phone": "+91 98201 12345",
                    "email": "aanya.sharma@example.com",
                    "address": "402 Oberoi Woods, Goregaon East, Mumbai",
                    "delivery_date": "Today, 5:00 PM - 7:00 PM",
                    "delivery_slot": "Evening Slot",
                    "cake_message": "Happy 21st Birthday Aanya! 💖",
                    "items": "Belgian Dark Chocolate Truffle (1 kg) x 1",
                    "items_json": json.dumps([
                        {"name": "Belgian Dark Chocolate Truffle", "weight": "1 kg", "quantity": 1, "price": 799.0}
                    ]),
                    "subtotal": Decimal("799.00"),
                    "discount": Decimal("0.00"),
                    "delivery_fee": Decimal("0.00"),
                    "total": Decimal("799.00"),
                    "payment_method": "Razorpay (Online)",
                    "payment_status": "Paid",
                    "razorpay_payment_id": "pay_Oqk89s1bZa99Kq",
                    "order_status": "Decorating & Packing",
                },
                {
                    "customer_name": "Rohan Malhotra",
                    "phone": "+91 98112 87654",
                    "email": "rohan.m@example.com",
                    "address": "Villa 12, Palm Meadows, Whitefield, Bengaluru",
                    "delivery_date": "Tomorrow, 11:00 AM - 1:00 PM",
                    "delivery_slot": "Morning Slot",
                    "cake_message": "Happy Anniversary Mom & Dad! 🥂",
                    "items": "Lotus Biscoff Caramel Cheesecake (1 kg) x 1, Wild Blueberry Glaze Cheesecake (0.5 kg) x 1",
                    "items_json": json.dumps([
                        {"name": "Lotus Biscoff Caramel Cheesecake", "weight": "1 kg", "quantity": 1, "price": 899.0},
                        {"name": "Wild Blueberry Glaze Cheesecake", "weight": "0.5 kg", "quantity": 1, "price": 849.0}
                    ]),
                    "subtotal": Decimal("1748.00"),
                    "discount": Decimal("150.00"),
                    "delivery_fee": Decimal("0.00"),
                    "total": Decimal("1598.00"),
                    "payment_method": "Razorpay (Online)",
                    "payment_status": "Paid",
                    "razorpay_payment_id": "pay_Np81mXx3La65Tz",
                    "order_status": "Baking in Oven",
                },
                {
                    "customer_name": "Pooja Mehta",
                    "phone": "+91 99870 54321",
                    "email": "pooja.mehta@example.com",
                    "address": "B-14 Green Park Extension, New Delhi",
                    "delivery_date": "Today, 8:00 PM - 10:00 PM",
                    "delivery_slot": "Late Evening Slot",
                    "cake_message": "Best Boss Ever! 🎉",
                    "items": "Classic Red Velvet Royale (1 kg) x 1",
                    "items_json": json.dumps([
                        {"name": "Classic Red Velvet Royale", "weight": "1 kg", "quantity": 1, "price": 749.0}
                    ]),
                    "subtotal": Decimal("749.00"),
                    "discount": Decimal("0.00"),
                    "delivery_fee": Decimal("40.00"),
                    "total": Decimal("789.00"),
                    "payment_method": "Razorpay (Online)",
                    "payment_status": "Paid",
                    "razorpay_payment_id": "pay_Mq77uYy8Re42Bn",
                    "order_status": "Out for Delivery",
                },
                {
                    "customer_name": "Vikram Sen",
                    "phone": "+91 97410 99887",
                    "email": "vikram.sen@example.com",
                    "address": "Flat 704, Skyline Towers, Sector 48, Gurugram",
                    "delivery_date": "Yesterday",
                    "delivery_slot": "Evening Slot",
                    "cake_message": "Happy Farewell Vikram!",
                    "items": "Ferrero Rocher Hazelnut Crunch (1.5 kg) x 1",
                    "items_json": json.dumps([
                        {"name": "Ferrero Rocher Hazelnut Crunch", "weight": "1.5 kg", "quantity": 1, "price": 949.0}
                    ]),
                    "subtotal": Decimal("949.00"),
                    "discount": Decimal("100.00"),
                    "delivery_fee": Decimal("0.00"),
                    "total": Decimal("849.00"),
                    "payment_method": "Razorpay (Online)",
                    "payment_status": "Paid",
                    "razorpay_payment_id": "pay_Kp62tVv1Qw90Mn",
                    "order_status": "Delivered",
                }
            ]

            for o in sample_orders:
                Order.objects.create(**o)
            self.stdout.write(self.style.SUCCESS("Sample orders created for dashboard stats."))
