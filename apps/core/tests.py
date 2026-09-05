import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from apps.packages.models import InternetPackage, PackageSubscription, calculate_expiry_date, calculate_custom_price
from apps.payments.models import Payment
from apps.payments.pdf_generator import generate_receipt_pdf, generate_history_pdf
from apps.accounts.models import UserProfile

class HAM 3WiFiPlatformTests(TestCase):
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
            price=Decimal('2000.00'),
            description='High performance fiber',
            is_featured=True,
            is_active=True
        )

    def test_expiry_date_calculation_rule(self):
        """
        Verify that expiry date is ALWAYS calculated as the 8th of the next month.
        Example: September 15 -> October 8
        """
        d1 = datetime.date(2026, 9, 15)
        e1 = calculate_expiry_date(d1)
        self.assertEqual(e1, datetime.date(2026, 10, 8))

        # Year rollover: December 20, 2026 -> January 8, 2027
        d2 = datetime.date(2026, 12, 20)
        e2 = calculate_expiry_date(d2)
        self.assertEqual(e2, datetime.date(2027, 1, 8))

        # Early month: January 5, 2026 -> February 8, 2026
        d3 = datetime.date(2026, 1, 5)
        e3 = calculate_expiry_date(d3)
        self.assertEqual(e3, datetime.date(2026, 2, 8))

    def test_public_pages_render(self):
        """Verify that public pages render with HTTP 200"""
        for url in ['/', '/packages/', '/about/', '/contact/', '/login/', '/register/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed on {url}")
            self.assertContains(response, 'HAM 3')

    def test_allauth_user_registration_login_logout_sessions(self):
        """
        Verify Allauth registration, profile persistence, session retention,
        logout, and multi-credential login (username & email).
        """
        # 1. Register new customer
        post_data = {
            'first_name': 'Ahmad',
            'last_name': 'Khan',
            'username': 'ahmad_khan',
            'email': 'ahmad@example.com',
            'phone_number': '03451122334',
            'whatsapp_number': '03451122334',
            'address': 'Main Optical Fiber Lane, HAM 3',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        reg_resp = self.client.post('/register/', post_data, follow=True)
        self.assertEqual(reg_resp.status_code, 200)

        # 2. Verify user in database
        ahmad = User.objects.filter(username='ahmad_khan').first()
        self.assertIsNotNone(ahmad)
        self.assertEqual(ahmad.email, 'ahmad@example.com')
        self.assertEqual(ahmad.profile.phone_number, '03451122334')

        # 3. Verify user appears in Admin Portal
        self.client.force_login(self.admin)
        admin_users_resp = self.client.get('/admin/auth/user/')
        self.assertEqual(admin_users_resp.status_code, 200)
        self.assertContains(admin_users_resp, 'ahmad_khan')

        # 4. Verify session persistence for customer across navigation
        self.client.logout()
        # Login with username
        login_resp = self.client.post('/login/', {'login': 'ahmad_khan', 'password': 'StrongPass123!'}, follow=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)

        # Navigating to pages keeps customer logged in
        dash_resp = self.client.get('/dashboard/')
        self.assertEqual(dash_resp.status_code, 200)
        order_resp = self.client.get('/packages/order/')
        self.assertEqual(order_resp.status_code, 200)

        # 5. Logout
        logout_resp = self.client.post('/logout/', follow=True)
        self.assertEqual(logout_resp.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

        # 6. Login with email
        email_login_resp = self.client.post('/login/', {'login': 'ahmad@example.com', 'password': 'StrongPass123!'}, follow=True)
        self.assertEqual(email_login_resp.status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)

    def test_easypaisa_gateway_and_activation_flow(self):
        """
        Verify the complete EasyPaisa gateway flow:
        Select Package -> EasyPaisa Gateway -> Activate Package -> WhatsApp & Status Notice.
        """
        self.client.force_login(self.user)

        # 1. User orders package from wizard
        order_post = self.client.post('/packages/order/', {
            'package_id': self.pkg20.id,
            'purchase_date': '2026-09-15',
        })
        self.assertEqual(order_post.status_code, 302)

        # Should redirect to dedicated EasyPaisa Gateway page
        sub = PackageSubscription.objects.filter(user=self.user, status='pending').first()
        self.assertIsNotNone(sub)
        expected_gateway_url = f'/payments/gateway/{sub.id}/'
        self.assertEqual(order_post.url, expected_gateway_url)

        # 2. Load EasyPaisa Gateway page
        gateway_resp = self.client.get(expected_gateway_url)
        self.assertEqual(gateway_resp.status_code, 200)
        # Verify EasyPaisa admin account and details are automatically displayed
        self.assertContains(gateway_resp, '03452524086')
        self.assertContains(gateway_resp, 'HAM 3 NETWORK')
        self.assertContains(gateway_resp, '2000')

        # 3. User clicks Return to Website / Activate Package screen
        activate_url = f'/payments/activate/{sub.id}/'
        activate_get = self.client.get(activate_url)
        self.assertEqual(activate_get.status_code, 200)
        self.assertContains(activate_get, 'Activate Your')

        # 4. User submits TRX ID and sender number
        activate_post = self.client.post(activate_url, {
            'sender_number': '03001234567',
            'transaction_id': 'EP-8899001122',
        }, follow=True)
        self.assertEqual(activate_post.status_code, 200)

        # 5. Verify payment created with pending status
        payment = Payment.objects.filter(transaction_id='EP-8899001122').first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.verification_status, 'pending')

        # 6. Verify required message and admin WhatsApp link
        self.assertContains(activate_post, 'Your package is being activated. Please wait.')
        self.assertContains(activate_post, '03452524086')
        self.assertContains(activate_post, 'Share Proof with Admin on WhatsApp')

    def test_payment_verification_and_activation(self):
        """Test admin verification in Admin Portal activates subscription and updates dashboard"""
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

        # Admin activates payment
        payment.verify_and_activate(admin_user=self.admin)
        payment.refresh_from_db()
        sub.refresh_from_db()

        self.assertEqual(payment.verification_status, 'verified')
        self.assertEqual(sub.status, 'active')
        self.assertIsNotNone(sub.activation_date)

        # Check dashboard as user
        self.client.force_login(self.user)
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
        self.assertEqual(calculate_custom_price(2), Decimal('560'))
        self.assertEqual(calculate_custom_price(10), Decimal('1200'))
        self.assertEqual(calculate_custom_price(15), Decimal('1600'))
        self.assertEqual(calculate_custom_price(20), Decimal('2000'))
        self.assertEqual(calculate_custom_price(30), Decimal('2800'))
        self.assertEqual(calculate_custom_price(1), Decimal('560'))
        self.assertEqual(calculate_custom_price(50), Decimal('2800'))

        resp = self.client.get('/packages/api/calculate-custom-price/?speed=18')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['speed'], 18)
        self.assertEqual(data['price'], 1840.0)
