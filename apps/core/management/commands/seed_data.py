import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from apps.accounts.models import UserProfile
from apps.packages.models import InternetPackage, PackageSubscription, calculate_expiry_date
from apps.payments.models import Payment
from apps.core.models import SpecialOffer, Feedback
from apps.complaints.models import Complaint
from apps.notifications.models import Notification

class Command(BaseCommand):
    help = 'Seed initial packages, offers, feedback, and demo users for Mehran WiFi Service'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Mehran WiFi Service initial data..."))

        # 1. Superuser
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@mehranwifi.com',
                'first_name': 'Mehran',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created (password: admin123)"))
        else:
            self.stdout.write(self.style.WARNING("Superuser 'admin' already exists"))

        # Admin profile
        if hasattr(admin_user, 'profile'):
            admin_user.profile.phone_number = '03454524086'
            admin_user.profile.whatsapp_number = '03454524086'
            admin_user.profile.address = 'Mehran WiFi NOC Headquarters'
            admin_user.profile.save()

        # 2. Demo customer
        demo_user, created = User.objects.get_or_create(
            username='demo_customer',
            defaults={
                'email': 'customer@gmail.com',
                'first_name': 'Ali',
                'last_name': 'Khan',
            }
        )
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS("Demo user 'demo_customer' created (password: demo123)"))
        
        if hasattr(demo_user, 'profile'):
            demo_user.profile.phone_number = '03001234567'
            demo_user.profile.whatsapp_number = '03001234567'
            demo_user.profile.address = 'House 42, Block B, Mehran Colony'
            demo_user.profile.save()

        # 3. Internet Packages
        packages_data = [
            {
                'name': '10 Mbps Fiber Starter',
                'speed_mbps': 10,
                'price': 1200.00,
                'description': 'Ideal for individual users, web browsing, social media, and smooth music/video streaming.',
                'features': '',
                'is_featured': False,
                'display_order': 1,
            },
            {
                'name': '15 Mbps Fiber Stream',
                'speed_mbps': 15,
                'price': 1600.00,
                'description': 'Perfect for small families with multi-device connections, online schooling, and HD streaming.',
                'features': '',
                'is_featured': False,
                'display_order': 2,
            },
            {
                'name': '20 Mbps Fiber Pro',
                'speed_mbps': 20,
                'price': 2000.00,
                'description': 'Our most popular plan! Blazing speeds for 4K streaming, multi-user gaming, and heavy downloads.',
                'features': '',
                'is_featured': True,
                'display_order': 3,
            },
            {
                'name': '30 Mbps Ultra Turbo',
                'speed_mbps': 30,
                'price': 2800.00,
                'description': 'Designed for tech enthusiasts, heavy streamers, streamers, and work-from-home pros.',
                'features': '',
                'is_featured': False,
                'display_order': 4,
            },
            {
                'name': '50 Mbps Enterprise Fiber',
                'speed_mbps': 50,
                'price': 4500.00,
                'description': 'Maximum fiber throughput for power creators, smart homes, studios, and small offices.',
                'features': "Unlimited High-Speed Fiber Data\nCommercial-Grade Dual-Core Optical Terminal\nSymmetric Upload / Download Speeds\nDedicated Public IP Option\nSLA 99.9% Uptime Guarantee\nInstant On-Site Support Response",
                'is_featured': False,
                'display_order': 5,
            },
        ]

        created_packages = {}
        for pdata in packages_data:
            pkg, _ = InternetPackage.objects.update_or_create(
                speed_mbps=pdata['speed_mbps'],
                defaults=pdata
            )
            created_packages[pkg.speed_mbps] = pkg
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(packages_data)} Fiber Internet Packages."))

        # 4. Special Offers
        offers_data = [
            {
                'title': 'Free Optical Fiber Installation & ONT Router',
                'subtitle': 'Subscribe to any 3-month advance package and pay zero setup charges!',
                'discount_tag': 'ZERO SETUP FEE',
                'description': 'Get free optical drop cable wiring (up to 150m) and a free gigabit optical terminal with any 3-month advance subscription.',
                'target_package': created_packages.get(20),
            },
            {
                'title': 'Midnight Double Speed Turbo Boost',
                'subtitle': 'Enjoy 2X download speed every night between 12:00 AM and 8:00 AM!',
                'discount_tag': 'NIGHT TURBO',
                'description': 'All 20 Mbps and higher fiber packages automatically upgrade to double bandwidth during off-peak night hours with zero extra charge.',
                'target_package': created_packages.get(30),
            },
            {
                'title': 'EasyPaisa Instant Activation Bonus',
                'subtitle': 'Pay seamlessly using EasyPaisa to 03454524086 for priority queue verification!',
                'discount_tag': 'EASYPAISA VIP',
                'description': 'Direct EasyPaisa digital payments receive automated priority processing and instant activation within 15 minutes.',
                'target_package': created_packages.get(15),
            },
        ]

        for odata in offers_data:
            SpecialOffer.objects.get_or_create(
                title=odata['title'],
                defaults=odata
            )
        self.stdout.write(self.style.SUCCESS("Loaded Special Offers."))

        # 5. Feedbacks
        feedbacks_data = [
            {
                'name': 'Muhammad Tariq',
                'email': 'tariq@gmail.com',
                'rating': 5,
                'message': 'Mehran WiFi Service is unmatched in our area! The 20 Mbps Fiber Pro package gives constant 20 Mbps speeds day and night without disconnection. EasyPaisa payment makes it so simple to pay every month.',
                'is_approved': True
            },
            {
                'name': 'Zainab Bibi',
                'email': 'zainab.b@yahoo.com',
                'rating': 5,
                'message': 'My children attend online classes and I work remotely. The fiber connection latency is ultra-smooth on Zoom and Teams. Customer support team is always helpful and polite.',
                'is_approved': True
            },
            {
                'name': 'Engr. Bilal Memon',
                'email': 'bilal.memon@outlook.com',
                'rating': 5,
                'message': 'Low ping on PUBG and Valorant! Finally an ISP that understands routing and gives true optical fiber directly to the home. The digital receipt feature on WhatsApp is great.',
                'is_approved': True
            },
        ]

        for fdata in feedbacks_data:
            Feedback.objects.get_or_create(
                email=fdata['email'],
                defaults=fdata
            )
        self.stdout.write(self.style.SUCCESS("Loaded Customer Feedback."))

        # 6. Sample Demo User Active Subscription & Payment
        pkg20 = created_packages.get(20)
        today = datetime.date.today()
        # Next month's 8th
        expiry = calculate_expiry_date(today)

        # Check if demo_user already has subscription
        if not PackageSubscription.objects.filter(user=demo_user).exists():
            sub = PackageSubscription.objects.create(
                user=demo_user,
                package=pkg20,
                package_name_snapshot=pkg20.name,
                speed_snapshot=pkg20.speed_mbps,
                price_snapshot=pkg20.price,
                purchase_date=today,
                activation_date=timezone.now(),
                expiry_date=expiry,
                status='active'
            )

            payment = Payment.objects.create(
                user=demo_user,
                subscription=sub,
                amount=pkg20.price,
                payment_method='EasyPaisa',
                easypaisa_number='03454524086',
                sender_number='03001234567',
                transaction_id='EP-7894561230',
                payment_date=timezone.now(),
                verification_status='verified',
                verified_by=admin_user,
                verified_at=timezone.now(),
                admin_notes='Verified via EasyPaisa Merchant SMS'
            )

            Notification.objects.create(
                user=demo_user,
                title="🟢 Welcome to Mehran WiFi Service!",
                message=f"Your {pkg20.name} (20 Mbps) is active until {expiry.strftime('%B 8, %Y')}. Thank you for choosing Mehran WiFi!",
                link="/dashboard/"
            )

            self.stdout.write(self.style.SUCCESS("Created demo active subscription and verified payment for 'demo_customer'."))

        self.stdout.write(self.style.SUCCESS("=== Seeding completed successfully! ==="))
