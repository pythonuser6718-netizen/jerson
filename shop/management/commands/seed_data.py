from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Category, Brand, Product


class Command(BaseCommand):
    help = "Seed the database with sample categories, brands, and phones."

    def handle(self, *args, **options):
        categories = ['Smartphones', 'Budget Phones', 'Flagship', 'Accessories']
        brands = ['Apple', 'Samsung', 'OnePlus', 'Xiaomi', 'Google']

        cat_objs = {}
        for name in categories:
            cat, _ = Category.objects.get_or_create(name=name, slug=slugify(name))
            cat_objs[name] = cat

        brand_objs = {}
        for name in brands:
            brand, _ = Brand.objects.get_or_create(name=name)
            brand_objs[name] = brand

        products = [
            ("iPhone 16", "Apple", "Flagship", 79999, None, "8GB", "128GB", "Black", True,
             "Apple's latest flagship with the A18 chip, a stunning OLED display, and all-day battery life."),
            ("iPhone 15", "Apple", "Smartphones", 69999, 64999, "6GB", "128GB", "Blue", False,
             "A reliable, fast iPhone with a great camera system at a friendlier price."),
            ("Galaxy S25 Ultra", "Samsung", "Flagship", 124999, None, "12GB", "256GB", "Titanium Gray", True,
             "Samsung's top-tier flagship with S Pen support and a pro-grade camera setup."),
            ("Galaxy A55", "Samsung", "Budget Phones", 32999, 28999, "8GB", "128GB", "Awesome Navy", False,
             "A well-rounded mid-ranger with a bright AMOLED screen and long battery life."),
            ("OnePlus 13", "OnePlus", "Flagship", 69999, None, "16GB", "256GB", "Midnight Ocean", True,
             "Blazing-fast performance, Hasselblad cameras, and 100W fast charging."),
            ("OnePlus Nord 5", "OnePlus", "Smartphones", 27999, None, "8GB", "128GB", "Marble Teal", False,
             "Flagship-inspired design and smooth performance for everyday use."),
            ("Redmi Note 14 Pro", "Xiaomi", "Budget Phones", 21999, 18999, "8GB", "128GB", "Forest Green", False,
             "Excellent value with a 200MP camera and a durable curved display."),
            ("Xiaomi 15", "Xiaomi", "Flagship", 64999, None, "12GB", "256GB", "Black", False,
             "A compact flagship packed with Leica optics and top-tier performance."),
            ("Pixel 9", "Google", "Smartphones", 59999, 54999, "8GB", "128GB", "Porcelain", True,
             "Pure Android experience with best-in-class computational photography."),
            ("Pixel 9a", "Google", "Budget Phones", 39999, None, "8GB", "128GB", "Iris", False,
             "Google's affordable Pixel with the same great camera smarts."),
        ]

        for name, brand, cat, price, discount, ram, storage, color, featured, desc in products:
            slug = slugify(name)
            Product.objects.update_or_create(
                slug=slug,
                defaults=dict(
                    name=name,
                    brand=brand_objs[brand],
                    category=cat_objs[cat],
                    price=price,
                    discount_price=discount,
                    ram=ram,
                    storage=storage,
                    color=color,
                    stock=25,
                    is_active=True,
                    is_featured=featured,
                    description=desc,
                )
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(products)} products across {len(categories)} categories."))
