from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.packages.models import InternetPackage
from apps.accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Seeds initial internet packages and default admin/customer accounts'

    def handle(self, *args, **options):
        # 1. Seed Packages
        packages_data = [
            {
                'name': '10 Mbps Fiber Starter',
                'speed_mbps': 10,
                'price': Decimal('1200.00'),
                'description': 'Ideal for light browsing, HD streaming, and everyday home connectivity.',
                'features': 'Unlimited High-Speed Fiber Data\nSingle-Band WiFi Router Included\nYouTube HD & Social Media Streaming\n99.5% Network Reliability',
                'is_featured': False,
                'is_custom': False,
                'display_order': 1,
            },
            {
                'name': '15 Mbps Fast Stream',
                'speed_mbps': 15,
                'price': Decimal('1600.00'),
                'description': 'Enhanced optical bandwidth for seamless multitasking and 1080p video streaming.',
                'features': 'Unlimited High-Speed Fiber Data\nDual-Band Optical Terminal\nBuffer-Free Full HD Streaming\nLow Latency Gaming\n24/7 Priority Support',
                'is_featured': False,
                'is_custom': False,
                'display_order': 2,
            },
            {
                'name': '20 Mbps Fiber Pro',
                'speed_mbps': 20,
                'price': Decimal('2000.00'),
                'description': 'Ultra-low ping and high throughput for competitive gaming and multiple devices.',
                'features': 'Unlimited High-Speed Fiber Data\nDual-Band Optical Terminal\nLow Latency Gaming (<15ms NOC)\nMulti-Device Ultra Performance\nInstant EasyPaisa Verification',
                'is_featured': True,
                'is_custom': False,
                'display_order': 3,
            },
            {
                'name': '30 Mbps Ultra Turbo',
                'speed_mbps': 30,
                'price': Decimal('2800.00'),
                'description': 'High-performance fiber connection for heavy downloads, 4K streaming, and multi-user households.',
                'features': 'Unlimited High-Speed Fiber Data\nGigabit Optical Gateway\nSimultaneous 4K Ultra HD Streaming\nLowest Ping Competitive Esports\nDedicated NOC Bandwidth Pipe',
                'is_featured': False,
                'is_custom': False,
                'display_order': 4,
            },
            {
                'name': 'Custom Fiber Package',
                'speed_mbps': 2,
                'price': Decimal('560.00'),
                'description': 'Design your own optical fiber package from 2 Mbps up to 30 Mbps with instant monthly pricing.',
                'features': 'Flexible 2 Mbps to 30 Mbps Bandwidth\nInstant Dynamic Pricing (Rs. 400 + Rs. 80/Mbps)\nEasyPaisa Instant Activation\nMonthly Renewal on 8th of Next Month\nDedicated Mehran NOC Support',
                'is_featured': False,
                'is_custom': True,
                'display_order': 5,
            },
        ]

        for pdata in packages_data:
            pkg, created = InternetPackage.objects.get_or_create(
                name=pdata['name'],
                defaults=pdata
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created package: {pkg.name}"))
            else:
                for k, v in pdata.items():
                    setattr(pkg, k, v)
                pkg.save()
                self.stdout.write(f"Updated package: {pkg.name}")

        # 2. Seed Admin User
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@mehranwifi.com',
                password='adminpassword',
                first_name='NOC',
                last_name='Manager'
            )
            profile, _ = UserProfile.objects.get_or_create(user=admin_user)
            profile.phone_number = '03454524086'
            profile.whatsapp_number = '03454524086'
            profile.address = 'Main Optical Fiber Hub, Mehran City'
            profile.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / adminpassword"))

        # 3. Seed Demo Customer
        if not User.objects.filter(username='demo_customer').exists():
            demo_user = User.objects.create_user(
                username='demo_customer',
                email='customer@gmail.com',
                password='demo123',
                first_name='Demo',
                last_name='Customer'
            )
            profile, _ = UserProfile.objects.get_or_create(user=demo_user)
            profile.phone_number = '03001234567'
            profile.whatsapp_number = '03001234567'
            profile.address = 'House 12, Street 4, Sector B, Mehran City'
            profile.save()
            self.stdout.write(self.style.SUCCESS("Created demo customer: demo_customer / demo123"))

        self.stdout.write(self.style.SUCCESS("All seed data successfully verified!"))
