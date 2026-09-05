import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from apps.packages.models import InternetPackage, PackageSubscription, calculate_expiry_date
from apps.payments.models import Payment
from apps.payments.pdf_generator import generate_receipt_pdf, generate_history_pdf
from apps.complaints.models import Complaint

class MehranWiFiPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Create user
        self.user = User.objects.create_user(
            username='test_customer',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='Customer'
        )
        self.user.profile.phone_number = '03001234567'
        self.user.profile.whatsapp_number = '03001234567'
        self.user.profile.save()

        # 2. Create staff admin
        self.admin = User.objects.create_superuser(
            username='test_admin',
            email='admin@mehranwifi.com',
            password='adminpassword',
            first_name='NOC',
            last_name='Admin'
        )

        # 3. Create sample packages
        self.pkg20 = InternetPackage.objects.create(
            name='20 Mbps Fiber Pro',
            speed_mbps=20,
            price=2000.00,
            description='High performance fiber',
            is_featured=True,
            is_active=True
        )

    def test_expiry_date_calculation_rule(self):
        """
        Verify that expiry date is ALWAYS calculated as the 8th of the next month.
        Example in prompt: September 15 -> October 8
        """
        # Test September 15, 2026
        d1 = datetime.date(2026, 9, 15)
        e1 = calculate_expiry_date(d1)
        self.assertEqual(e1, datetime.date(2026, 10, 8))

        # Test December 20, 2026 -> January 8, 2027 (year rollover)
        d2 = datetime.date(2026, 12, 20)
        e2 = calculate_expiry_date(d2)
        self.assertEqual(e2, datetime.date(2027, 1, 8))

        # Test January 5, 2026 -> February 8, 2026
        d3 = datetime.date(2026, 1, 5)
        e3 = calculate_expiry_date(d3)
        self.assertEqual(e3, datetime.date(2026, 2, 8))

    def test_public_pages_render(self):
        """Verify that public pages render with HTTP 200"""
        for url in ['/', '/packages/', '/about/', '/contact/', '/login/', '/register/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed on {url}")
            self.assertContains(response, 'Mehran')

    def test_package_ordering_wizard_flow(self):
        """Test ordering a package with EasyPaisa details and verify pending state"""
        self.client.login(username='test_customer', password='password123')

        response = self.client.post('/packages/order/', {
            'package_id': self.pkg20.id,
            'purchase_date': '2026-09-15',
            'sender_number': '03001234567',
            'transaction_id': 'EP-9988776655',
        })

        # Should redirect to receipt page
        self.assertEqual(response.status_code, 302)
        payment = Payment.objects.filter(transaction_id='EP-9988776655').first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.verification_status, 'pending')
        self.assertEqual(payment.subscription.status, 'pending')
        self.assertEqual(payment.subscription.expiry_date, datetime.date(2026, 10, 8))

        # Follow redirect to receipt
        receipt_response = self.client.get(response.url)
        self.assertEqual(receipt_response.status_code, 200)
        self.assertContains(receipt_response, 'Your payment is under verification')
        self.assertContains(receipt_response, '03454524086')

    def test_payment_verification_and_activation(self):
        """Test admin verification activates subscription and sets green status"""
        p_date = datetime.date(2026, 9, 15)
        sub = PackageSubscription.objects.create(
            user=self.user,
            package=self.pkg20,
            package_name_snapshot=self.pkg20.name,
            speed_snapshot=self.pkg20.speed_mbps,
            price_snapshot=self.pkg20.price,
            purchase_date=p_date,
            expiry_date=calculate_expiry_date(p_date),
            status='pending'
        )
        payment = Payment.objects.create(
            user=self.user,
            subscription=sub,
            amount=self.pkg20.price,
            transaction_id='EP-TEST-VERIFY',
            verification_status='pending'
        )

        # Execute verify and activate
        payment.verify_and_activate(admin_user=self.admin)
        payment.refresh_from_db()
        sub.refresh_from_db()

        self.assertEqual(payment.verification_status, 'verified')
        self.assertEqual(sub.status, 'active')
        self.assertIsNotNone(sub.activation_date)

        # Check dashboard as user
        self.client.login(username='test_customer', password='password123')
        dash_response = self.client.get('/dashboard/')
        self.assertEqual(dash_response.status_code, 200)
        self.assertContains(dash_response, 'PACKAGE ACTIVE')
        self.assertContains(dash_response, '20 Mbps')

    def test_pdf_generators(self):
        """Test that ReportLab receipt and history PDFs generate valid PDF bytes"""
        p_date = datetime.date(2026, 9, 15)
        sub = PackageSubscription.objects.create(
            user=self.user,
            package=self.pkg20,
            package_name_snapshot=self.pkg20.name,
            speed_snapshot=self.pkg20.speed_mbps,
            price_snapshot=self.pkg20.price,
            purchase_date=p_date,
            expiry_date=calculate_expiry_date(p_date),
            status='active'
        )
        payment = Payment.objects.create(
            user=self.user,
            subscription=sub,
            amount=self.pkg20.price,
            transaction_id='EP-TEST-PDF',
            verification_status='verified'
        )

        # Receipt PDF
        receipt_pdf = generate_receipt_pdf(payment)
        self.assertTrue(len(receipt_pdf) > 1000)
        self.assertTrue(receipt_pdf.startswith(b'%PDF'))

        # History PDF
        history_pdf = generate_history_pdf(self.user, PackageSubscription.objects.filter(user=self.user))
        self.assertTrue(len(history_pdf) > 1000)
        self.assertTrue(history_pdf.startswith(b'%PDF'))

    def test_custom_package_calculation_and_order(self):
        """Test custom package calculation formula, clamping, API and ordering wizard flow"""
        from apps.packages.models import calculate_custom_price
        from decimal import Decimal

        # 1. Test calculation formula: 400 + (speed * 80)
        self.assertEqual(calculate_custom_price(2), Decimal('560'))
        self.assertEqual(calculate_custom_price(10), Decimal('1200'))
        self.assertEqual(calculate_custom_price(15), Decimal('1600'))
        self.assertEqual(calculate_custom_price(20), Decimal('2000'))
        self.assertEqual(calculate_custom_price(30), Decimal('2800'))
        # Clamping
        self.assertEqual(calculate_custom_price(1), Decimal('560'))
        self.assertEqual(calculate_custom_price(50), Decimal('2800'))

        # 2. Test API calculate-custom-price
        resp = self.client.get('/packages/api/calculate-custom-price/?speed=18')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['speed'], 18)
        self.assertEqual(data['price'], 1840.0)

        # 3. Create a custom package in database
        custom_pkg = InternetPackage.objects.create(
            name='Custom Fiber Package',
            speed_mbps=2,
            price=Decimal('560.00'),
            description='Flexible custom bandwidth from 2 to 30 Mbps',
            is_custom=True,
            is_active=True
        )

        # 4. Order custom package with custom speed 18 Mbps
        self.client.login(username='test_customer', password='password123')
        post_resp = self.client.post('/packages/order/', {
            'package_id': custom_pkg.id,
            'custom_speed': 18,
            'purchase_date': '2026-09-10',
            'sender_number': '03001234567',
            'transaction_id': 'EP-CUSTOM-18MB',
        })
        self.assertEqual(post_resp.status_code, 302)

        payment = Payment.objects.filter(transaction_id='EP-CUSTOM-18MB').first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, Decimal('1840.00'))
        self.assertEqual(payment.subscription.speed_snapshot, 18)
        self.assertEqual(payment.subscription.package_name_snapshot, 'Custom 18 Mbps Fiber Plan')
        self.assertEqual(payment.subscription.price_snapshot, Decimal('1840.00'))
        self.assertEqual(payment.subscription.expiry_date, datetime.date(2026, 10, 8))

