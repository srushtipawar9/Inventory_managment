import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile

def setup_admin():
    print("Checking admin user setup...")
    
    # 1. Create or get superuser 'admin'
    admin_user, created = User.objects.get_or_create(username='admin')
    admin_user.set_password('Pruthvi@15')
    admin_user.email = 'admin@pruthviraj.com'
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()

    if created:
        print("Created new superuser: admin / Pruthvi@15")
    else:
        print("Superuser 'admin' already exists. Password updated to Pruthvi@15.")
        
    # 2. Create Profile associated with 'admin' if not present
    profile, p_created = Profile.objects.get_or_create(user=admin_user)
    if p_created:
        print("Created Profile associated with admin user.")
    else:
        print("Profile for admin user already exists.")
        
    print("Setup completed successfully!")

if __name__ == '__main__':
    setup_admin()
