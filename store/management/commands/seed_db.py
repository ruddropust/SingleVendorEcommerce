from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product

class Command(BaseCommand):
    help = 'Seeds the database with initial categories and products'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created with password 'adminpass123'"))

        # Create Categories
        cats = {
            'Laptops & Computers': 'High-performance workstations and ultraportable devices.',
            'Audio & Sound': 'Wireless noise-cancelling headphones and studio speakers.',
            'Smart Home': 'Intelligent assistants, light packs, and smart locks.'
        }
        
        category_objs = {}
        for cat_name, desc in cats.items():
            cat, created = Category.objects.get_or_create(name=cat_name)
            category_objs[cat_name] = cat
            if created:
                self.stdout.write(f"Category '{cat_name}' created.")

        # Create Products
        products = [
            {
                'category': category_objs['Laptops & Computers'],
                'name': 'AuraBook Pro 14',
                'description': 'Unleash next-generation computing with our flagship 14-inch developer laptop. Built with a 10-core chip, 32GB unified memory, and 1TB SSD. Featuring a gorgeous liquid retina display and up to 20 hours of battery life.',
                'price': 1499.00,
                'stock': 12,
            },
            {
                'category': category_objs['Laptops & Computers'],
                'name': 'Zenith Mini Workstation',
                'description': 'Power in a compact frame. The Zenith Mini houses a 12-core processor, discrete graphics card capability, and silent cooling loops. Ideal for software developers, video editors, and power users who value desk space.',
                'price': 899.99,
                'stock': 8,
            },
            {
                'category': category_objs['Audio & Sound'],
                'name': 'SonicWave Noise-Cancelling Headphones',
                'description': 'Experience pure silence and pristine acoustics. The SonicWave features hybrid active noise cancellation, custom-tuned high-excursion drivers, and 40-hour wireless battery life with rapid-charge capabilities.',
                'price': 299.00,
                'stock': 25,
            },
            {
                'category': category_objs['Audio & Sound'],
                'name': 'Pulse Studio Compact Speaker',
                'description': 'Rich, room-filling sound in a beautiful anodized aluminum housing. Connects via Bluetooth 5.2 or optical input. Includes smart equalizer calibration to match your room acoustics automatically.',
                'price': 149.50,
                'stock': 15,
            },
            {
                'category': category_objs['Smart Home'],
                'name': 'Beacon Smart Home Hub',
                'description': 'The brain of your modern household. Connect and control all Zigbee, Z-Wave, and Wi-Fi smart accessories from a centralized dashboard. Integrates with major voice assistants and runs local automation rules.',
                'price': 79.99,
                'stock': 5,
            },
            {
                'category': category_objs['Smart Home'],
                'name': 'Glow Bulb Duo Pack',
                'description': 'Enhance your room with customizable mood lighting. The Glow Bulb Duo contains two smart LED bulbs supporting millions of colors, scheduling, circadian cycle matching, and visual music syncing.',
                'price': 34.99,
                'stock': 50,
            },
            {
                'category': category_objs['Smart Home'],
                'name': 'Aura Smart Door Lock',
                'description': 'Keyless secure entrance using biometric fingerprint scanners, PIN codes, or phone proximity. Monitor activity, issue temporary codes, and lock/unlock from anywhere in the world.',
                'price': 199.00,
                'stock': 0, # Out of stock product for testing
            }
        ]

        for p_data in products:
            p, created = Product.objects.get_or_create(
                category=p_data['category'],
                name=p_data['name'],
                defaults={
                    'description': p_data['description'],
                    'price': p_data['price'],
                    'stock': p_data['stock']
                }
            )
            if created:
                self.stdout.write(f"Product '{p_data['name']}' created.")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
