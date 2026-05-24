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
    if created:
        admin_user.set_password('admin')
        admin_user.email = 'admin@pruthviraj.com'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print("Created new superuser: admin / admin")
    else:
        # Ensure superuser flags are active
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print("Superuser 'admin' already exists.")
        
    # 2. Create Profile associated with 'admin' if not present
    profile, p_created = Profile.objects.get_or_create(user=admin_user)
    if p_created:
        print("Created Profile associated with admin user.")
    else:
        print("Profile for admin user already exists.")
        
    print("Setup completed successfully!")

if __name__ == '__main__':
    setup_admin()
