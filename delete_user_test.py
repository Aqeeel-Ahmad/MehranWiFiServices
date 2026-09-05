import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mehran_wifi.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Create superuser
User.objects.all().delete()
su = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
customer = User.objects.create_user('customer', 'cust@example.com', 'custpass')

client = Client()
client.login(username='admin', password='adminpass')

print("Session before delete:", client.session.keys())

# Fetch delete confirmation page
resp = client.get(f'/admin/auth/user/{customer.id}/delete/')
print("GET delete page status:", resp.status_code)

# Post to delete
resp2 = client.post(f'/admin/auth/user/{customer.id}/delete/', {'post': 'yes'}, follow=True)
print("POST delete status:", resp2.status_code)
print("Redirect chain:", resp2.redirect_chain)
print("Session after delete:", client.session.keys())
print("Customer exists:", User.objects.filter(username='customer').exists())
